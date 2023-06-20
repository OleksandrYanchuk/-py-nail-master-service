from datetime import time
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from nail_service.models import Services, User, Customer, Master, Events, PriceList


class ModelsTestCase(TestCase):

    def setUp(self):
        self.service = Services.objects.create(name="Test Service", price=Decimal('10.99'), time_service=time(10, 0))
        self.master = Master.objects.create(username="test_master", role=User.Role.MASTER)
        self.customer = Customer.objects.create(username="test_customer", role=User.Role.CUSTOMER)
        self.event = Events.objects.create(
            title="Test Event",
            start_date=timezone.make_aware(timezone.datetime(2023, 1, 1, 10, 0, 0)),
            end_date=timezone.make_aware(timezone.datetime(2023, 1, 1, 11, 0, 0)),
            master=self.master
        )
        self.price_list = PriceList.objects.create(
            master=self.master, service=self.service, price=Decimal('5.99'), time_service=time(0, 30)
        )

    def test_service_model(self):
        service = self.service
        self.assertEqual(service.name, "Test Service")
        self.assertEqual(service.price, Decimal('10.99'))
        self.assertEqual(service.time_service, time(10, 0))

    def test_master_model(self):
        master = self.master
        self.assertEqual(master.username, "test_master")
        self.assertEqual(master.role, User.Role.MASTER)
        self.assertEqual(master.services.count(), 1)

    def test_customer_model(self):
        customer = self.customer
        self.assertEqual(customer.username, "test_customer")
        self.assertEqual(customer.role, User.Role.CUSTOMER)
        self.assertEqual(customer.services.count(), 0)

    def test_events_model(self):
        event = self.event
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.start_date, timezone.make_aware(timezone.datetime(2023, 1, 1, 10, 0, 0)))
        self.assertEqual(event.end_date, timezone.make_aware(timezone.datetime(2023, 1, 1, 11, 0, 0)))
        self.assertEqual(event.master, self.master)

    def test_price_list_model(self):
        price_list = self.price_list
        self.assertEqual(price_list.master, self.master)
        self.assertEqual(price_list.service, self.service)
        self.assertEqual(price_list.price, Decimal('5.99'))
        self.assertEqual(price_list.time_service, time(0, 30))
