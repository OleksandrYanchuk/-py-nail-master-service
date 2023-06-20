from django.urls import path

from . import views
from .views import (
    index, MasterListView, MasterDetailView, MasterCreateView, MasterDeleteView, ServicesListView, CustomerListView,
    CustomerDetailView, CustomerCreateView, CustomerDeleteView, ServicesCreateView, ServicesUpdateView,
    ServicesDeleteView, MasterUpdateView, PriceListCreateView, PriceListUpdateView, PriceListDeleteView,
    CustomerUpdateView,
)


urlpatterns = [
    path("", index, name="index"),  
    path("master/", MasterListView.as_view(), name="master-list"),
    path(
        "master/<int:pk>/", MasterDetailView.as_view(), name="master-detail"
    ),
    path("master/", MasterListView.as_view(), name="master-list"),
    path("master/create/", MasterCreateView.as_view(), name="master-create"),
    path('master/<int:pk>/update/', MasterUpdateView.as_view(), name='master-update'),
    path(
        "master/<int:pk>/delete/",
        MasterDeleteView.as_view(),
        name="master-delete",
    ),
    path("services/", ServicesListView.as_view(), name="services-list"),
    path(
        "services/create/",
        ServicesCreateView.as_view(),
        name="services-create",
    ),
    path(
        "services/<int:pk>/update/",
        ServicesUpdateView.as_view(),
        name="services-update",
    ),
    path(
        "services/<int:pk>/delete/",
        ServicesDeleteView.as_view(),
        name="services-delete",
    ),
    path("customer/", CustomerListView.as_view(), name="customer-list"),
    path(
        "customer/<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"
    ),
    path('customer/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer-update'),
    path("customer/create/", CustomerCreateView.as_view(), name="customer-create"),
    path(
        "customer/<int:pk>/delete/",
        CustomerDeleteView.as_view(),
        name="customer-delete",
    ),
    path("all_events/", views.all_events, name="all_events"),
    path("add_event/", views.add_event, name="add_event"),
    path("update/", views.update, name="update"),
    path("remove/", views.remove, name="remove"),
    path("master/<int:pk>/create_price_list/", PriceListCreateView.as_view(), name="price-list-create"),
    path("master/<int:pk>/update_price_list/", PriceListUpdateView.as_view(), name="price-list-update"),
    path("master/<int:pk>/delete_price_list/", PriceListDeleteView.as_view(), name="price-list-delete"),
]

app_name = "nail_service"
