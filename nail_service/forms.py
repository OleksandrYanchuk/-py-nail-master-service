from django import forms
from django.contrib.auth import get_user_model

from django.contrib.auth.forms import UserCreationForm


from nail_service.models import Master, Customer, Services, PriceList


class MasterCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Master
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
        )


class MasterSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label=" ",
        widget=forms.TextInput(attrs={"placeholder": "Search master"})
    )


class ServicesCreateForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = "__all__"
        widgets = {
            "time_service": forms.TimeInput(format="%H:%M", attrs={"placeholder": "HH:MM"})
        }
        input_formats = ["%H:%M"]


class ServicesSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label=" ",
        widget=forms.TextInput(attrs={"placeholder": "Search name"})
    )


class CustomerSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label=" ",
        widget=forms.TextInput(attrs={"placeholder": "Search customer"})
    )


class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
        )


class PriceListForm(forms.ModelForm):

    class Meta:
        model = PriceList
        fields = "__all__"
