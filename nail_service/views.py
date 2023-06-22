from datetime import datetime
from typing import Any, Optional, Dict, List

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models import QuerySet
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponse, HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from .forms import (MasterCreationForm, MasterSearchForm, ServicesSearchForm,
                    CustomerSearchForm, CustomerCreationForm, ServicesCreateForm,
                    PriceListForm)
from .models import User, Services, Master, Customer, Events, PriceList


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View function for the home page of the site."""
    num_masters: int = Master.objects.count()
    num_customers: int = Customer.objects.count()
    num_visits: int = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_masters": num_masters,
        "num_customers": num_customers,
        "num_visits": num_visits + 1,
    }

    return render(request, "nail_service/index.html", context=context)


@login_required
def user_details(request) -> HttpResponseRedirect:
    """View function to handle user details based on their role."""
    user = request.user
    if request.user.role == User.Role.MASTER:
        # User has the 'Master' role
        return HttpResponseRedirect(f'/master/{user.pk}')
    elif request.user.role == User.Role.CUSTOMER:
        # User has the 'Customer' role
        return HttpResponseRedirect(f'/customer/{user.pk}')
    else:
        # User has no specific role assigned
        return render(request, 'nail_service/index.html')


def admin_required(view_func) -> callable:
    """
    Decorator function to check if the user has the 'Admin' role.
    Raises PermissionDenied if the user does not have the required role.
    """
    def wrapper(request, *args, **kwargs) -> callable:
        if request.user.role != User.Role.ADMIN:
            raise PermissionDenied("You do not have permission to perform this action.")
        return view_func(request, *args, **kwargs)
    return wrapper


def master_required(view_func) -> callable:
    """
    Decorator function to check if the user has the 'Master' role.
    Raises PermissionDenied if the user does not have the required role.
    """
    def wrapper(request, *args, **kwargs) -> callable:
        if request.user.role != User.Role.MASTER:
            raise PermissionDenied("You do not have permission to perform this action.")
        return view_func(request, *args, **kwargs)
    return wrapper


def customer_required(view_func) -> callable:
    """
    Decorator function to check if the user has the 'Customer' role.
    Raises PermissionDenied if the user does not have the required role.
    """
    def wrapper(request, *args, **kwargs) -> callable:
        if request.user.role != User.Role.CUSTOMER:
            raise PermissionDenied("You do not have permission to perform this action.")
        return view_func(request, *args, **kwargs)
    return wrapper


class MasterListView(LoginRequiredMixin, generic.ListView):
    """
    View class to display a list of masters.
    Requires user authentication.
    """
    model = Master
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context = super(MasterListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = MasterSearchForm(initial={"username": username})
        return context

    def get_queryset(self):
        queryset = Master.objects.filter(role="MASTER")
        form = MasterSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(username__icontains=form.cleaned_data["username"])

        return queryset.order_by("id")


class MasterUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    permission_required = "nail_service.change_own_master"
    model = Master
    form_class = MasterCreationForm
    success_url = reverse_lazy("nail_service:master-list")
    template_name = "nail_service/master_update_form.html"

    def form_valid(self, form) -> HttpResponse:
        """
        Performs additional operations when the form is valid.
        Saves the master object, updates the price list, and returns the result of the parent's form_valid method.
        """
        services = form.cleaned_data.get('services', [])
        self.object = form.save(commit=False)
        self.object.save()
        PriceList.objects.filter(master=self.object).delete()
        for service in services:
            price = form.cleaned_data.get('price_' + str(service.id))
            PriceList.objects.create(master=self.object, service=service, price=price)
        return super().form_valid(form)

    def test_func(self) -> bool:
        """
        Checks if the user has permission to update the master details.
        Returns True if the user matches the master's user, False otherwise.
        """
        return self.request.user == self.get_object().user

    def handle_no_permission(self) -> HttpResponse:
        """
        Handles the case when the user does not have permission to update the master details.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class MasterDetailView(LoginRequiredMixin, generic.DetailView):
    model = Master
    queryset = Master.objects.filter(role=User.Role.MASTER)
    template_name = 'nail_service/master_detail.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Adds event data to the context for displaying in the master detail page.
        """
        context = super().get_context_data(**kwargs)
        master = self.object

        events = Events.objects.filter(master_id=master.id).select_related("master")
        event_data = []
        for event in events:
            event_data.append({
                'title': event.title,
                'id': event.id,
                'start': event.start_date.strftime("%Y-%m-%d %H:%M:%S"),
                'end': event.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            })

        context['event_data'] = event_data
        return context


class MasterCreateView(generic.CreateView):
    model = Master
    form_class = MasterCreationForm
    success_url = reverse_lazy("nail_service:master-list")
    template_name = "nail_service/master_form.html"

    def form_valid(self, form) -> HttpResponse:
        """
        Performs additional operations when the form is valid.
        Saves the master object and updates the price list.
        Returns the result of the parent's form_valid method.
        """
        services = form.cleaned_data.get('services', [])
        self.object = form.save(commit=False)
        self.object.save()
        for service in services:
            price = form.cleaned_data.get('price_' + str(service.id))
            PriceList.objects.create(master=self.object, service=service, price=price)
        return super().form_valid(form)


class MasterDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    permission_required = "nail_service.change_own_master"
    model = Master
    success_url = reverse_lazy("nail_service:master-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to delete the master.
        Returns True if the user matches the master's user, False otherwise.
        """
        return self.request.user == self.get_object().user

    def handle_no_permission(self) -> HttpResponse:
        """
        Handles the case when the user does not have permission to delete the master.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class CustomerListView(LoginRequiredMixin, generic.ListView):
    model = Customer
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        """
        Adds search form to the context for displaying in the customer list page.
        """
        context = super().get_context_data(**kwargs)

        username = self.request.GET.get("username", "")

        context["search_form"] = CustomerSearchForm(initial={
            "username": username
        })

        return context

    def get_queryset(self) -> Any:
        """
        Returns the queryset of customers based on the search form's input.
        If the form is valid, filters the queryset based on the username.
        Otherwise, returns the queryset ordered by id.
        """
        queryset = Customer.objects.filter(role="CUSTOMER")
        form = CustomerSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(
                username__icontains=form.cleaned_data["username"]
            )

        return queryset.order_by("id")


class CustomerUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    permission_required = "nail_service.change_own_master"
    model = Customer
    form_class = CustomerCreationForm
    success_url = reverse_lazy("nail_service:customer-list")
    template_name = "nail_service/customer_update_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user has permission to update the customer details.
        Returns True if the user matches the customer's user, False otherwise.
        """
        return self.request.user == self.get_object().user

    def handle_no_permission(self) -> HttpResponse:
        """
        Handles the case when the user does not have permission to update the customer details.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class CustomerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Customer
    queryset = Customer.objects.all()


class CustomerCreateView(generic.CreateView):
    model = Customer
    form_class = CustomerCreationForm
    success_url = reverse_lazy("nail_service:customer-list")


class CustomerDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Customer
    success_url = reverse_lazy("nail_service:customer-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to delete the customer.
        Returns True if the user matches the customer's user, False otherwise.
        """
        return self.request.user == self.get_object().user

    def handle_no_permission(self) -> HttpResponse:
        """
        Handles the case when the user does not have permission to delete the customer.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class ServicesListView(LoginRequiredMixin, generic.ListView):
    model = Services
    context_object_name: str = "services_list"
    template_name: str = "nail_service/services_list.html"
    paginate_by: int = 5

    def get_context_data(self, *, object_list: Optional[QuerySet] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds search form to the context for displaying in the services list page.
        """
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")

        context["search_form"] = ServicesSearchForm(initial={
            "name": name,
        })

        return context

    def get_queryset(self) -> QuerySet:
        """
        Returns the queryset of services based on the search form's input.
        If the form is valid, filters the queryset based on the name.
        Otherwise, returns the queryset as is.
        """
        queryset = Services.objects.all()
        form = ServicesSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])

        return queryset


class ServicesCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Services
    form_class = ServicesCreateForm
    success_url = reverse_lazy("nail_service:services-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to create a service.
        Returns True if the user is a master and has a matching master object, False otherwise.
        """
        user = self.request.user
        if user.role == User.Role.MASTER:
            return user.master is not None and user.master == self.request.user.master
        return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user does not have permission to create a service.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class ServicesUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Services
    fields = "__all__"
    success_url = reverse_lazy("nail_service:services-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to update the service.
        Returns True if the user is a master and has a matching master object, False otherwise.
        """
        user = self.request.user
        if user.role == "ADMIN":
            return user is not None and user == self.request.user
        return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user does not have permission to update the service.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class ServicesDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Services
    success_url = reverse_lazy("nail_service:services-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to delete the service.
        Returns True if the user is a master and has a matching master object, False otherwise.
        """
        user = self.request.user
        if user.role == "ADMIN":
            return user is not None and user == self.request.user
        return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user does not have permission to delete the service.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class PriceListCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = PriceList
    form_class = PriceListForm
    success_url = reverse_lazy("nail_service:master-list")

    def form_valid(self, form: PriceListForm) -> HttpResponse:
        """
        Saves the form instance with the current user's master as the master for the price list.
        """
        form.instance.master = self.request.user.master
        return super().form_valid(form)

    def test_func(self) -> bool:
        """
        Checks if the user has permission to create a price list.
        Returns True if the user is a master and has a matching master object, False otherwise.
        """
        user = self.request.user
        if user.role == User.Role.MASTER:
            return user.master is not None and user.master == self.request.user.master
        return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user does not have permission to create a price list.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': self.get_permission_denied_message()
        }))


class PriceListUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = PriceList
    form_class = PriceListForm
    success_url = reverse_lazy("nail_service:master-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to update the price list.
        Returns True if the price list's master matches the user's master, False otherwise.
        """
        price_list = self.get_object()
        try:
            return price_list.master == self.request.user.master
        except ObjectDoesNotExist:
            return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user does not have permission to update the price list.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': "You do not have permission to update this price list."
        }))


class PriceListDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = PriceList
    success_url = reverse_lazy("nail_service:master-list")

    def test_func(self) -> bool:
        """
        Checks if the user has permission to delete the price list.
        Returns True if the price list's master matches the user's master, False otherwise.
        """
        price_list = self.get_object()
        try:
            return price_list.master == self.request.user.master
        except ObjectDoesNotExist:
            return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user does not have permission to delete the price list.
        Returns an HTTP Forbidden response with a rendered template for 403 error.
        """
        return HttpResponseForbidden(render_to_string('nail_service/403.html', {
            'error_message': "You do not have permission to delete this price list."
        }))


def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.title,
            'id': event.id,
            'start': event.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            'end': event.end_date.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)

@master_required
def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)

    start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

    user = request.user
    if user.role == User.Role.MASTER:
        master = user.master
        event = Events(title=title, start_date=start_date, end_date=end_date, master=master)
        event.save()

    data = {}
    return JsonResponse(data)


@master_required
def update(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    user = request.user
    if user.role == User.Role.MASTER and event.master == user.master:
        start = request.GET.get("start", None)
        end = request.GET.get("end", None)
        title = request.GET.get("title", None)
        event.start_date = start
        event.end_date = end
        event.title = title
        event.save()

    data = {}
    return JsonResponse(data)


@master_required
def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    user = request.user
    if user.role == User.Role.MASTER and event.master == user.master:
        event.delete()

    data = {}
    return JsonResponse(data)


@login_required
def subscribe_to_master(request, pk) -> HttpResponseRedirect:
    """
    Subscribes the current user to a specific master identified by the given ID.
    Returns an HTTP redirect response to the master's detail page.
    """
    customer = Customer.objects.get(user=request.user)
    master = get_object_or_404(Master, pk=pk)

    customer.master_customers.add(master)
    messages.success(request, "Successfully subscribed to the master.")

    return HttpResponseRedirect(reverse_lazy("nail_service:master-detail", args=[pk]))


@login_required
def unsubscribe_from_master(request, pk) -> HttpResponseRedirect:
    """
    Unsubscribes the current user from a specific master identified by the given ID.
    Returns an HTTP redirect response to the master's detail page.
    """
    customer = Customer.objects.get(user=request.user)
    master = get_object_or_404(Master, pk=pk)

    if master in customer.master_customers.all():
        customer.master_customers.remove(master)
        messages.success(request, "Successfully unsubscribed from the master.")
    else:
        messages.error(request, "You are not subscribed to this master.")

    return HttpResponseRedirect(reverse_lazy("nail_service:master-detail", args=[pk]))
