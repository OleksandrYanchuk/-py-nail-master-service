from django.db import models
from django.contrib.auth.models import AbstractUser

from django.urls import reverse


class Services(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=1000, decimal_places=2)
    time_service = models.TimeField(auto_now=False, auto_now_add=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} {self.price} {self.time_service}"


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        CUSTOMER = "CUSTOMER", 'Customer'
        MASTER = "MASTER", 'Master'

    base_role = Role.ADMIN

    role = models.CharField(max_length=50, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class Customer(User):
    base_role = User.Role.CUSTOMER

    services = models.ManyToManyField(Services, related_name="customer_services")
    masters = models.ManyToManyField('Master', related_name="customer_customers", verbose_name="Customer masters")

    user = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True)

    class Meta:
        ordering = ["id"]

    def get_absolute_url(self):
        return reverse("nail_service:customer-detail", kwargs={"pk": self.pk})


class Master(User):
    base_role = User.Role.MASTER

    user = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True)

    services = models.ManyToManyField(Services, related_name="master_services", through='PriceList')
    customers = models.ManyToManyField('Customer', related_name="master_customers", verbose_name="Master customers")

    class Meta:
        ordering = ["id"]
        permissions = [
            ("view_own_master", "Can view own master"),
            ("change_own_master", "Can change own master"),
            ("change_service_price", "Can change service price"),
        ]

    def get_absolute_url(self):
        return reverse("nail_service:master-detail", kwargs={"pk": self.pk})


class Events(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    master = models.ForeignKey(Master, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class PriceList(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=1000, decimal_places=2)
    time_service = models.TimeField(default=None, null=True, blank=True, auto_now=False, auto_now_add=False)

    class Meta:
        ordering = ["service"]

    def __str__(self):
        return f"Master: {self.master}, Service: {self.service}, Price: {self.price}, Time_for_service: {self.time_service}"
