from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from nail_service.models import User, Master, Customer


CUSTOMER_LIST_URL = reverse("nail_service:customer-list")


class PublicCustomerTests(TestCase):
    def test_login_required(self):
        client = Client()
        response = client.get(CUSTOMER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateCustomerTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(username="test_customer", role=User.Role.CUSTOMER)

        self.client = Client()
        self.client.force_login(self.customer)

    def test_index_view(self):
        url = reverse('nail_service:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nail_service/index.html')

    def test_customer_list_view(self):
        url = CUSTOMER_LIST_URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nail_service/customer_list.html')

    def test_customer_detail_view(self):
        url = reverse('nail_service:customer-detail', args=[self.customer.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nail_service/customer_detail.html')

    def test_master_list_view(self):
        url = reverse('nail_service:master-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nail_service/master_list.html')

    def test_master_detail_view(self):
        self.master = Master.objects.create(username="test_master", role=User.Role.MASTER)
        url = reverse('nail_service:master-detail', args=[self.master.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nail_service/master_detail.html')

    def test_create_customer(self):
        form_data = {
            "username": "Test_name1",
            "password1": "test_pass1234",
            "password2": "test_pass1234",
            "first_name": "Test_first",
            "last_name": "Test_last",
            "role": "CUSTOMER"
        }
        self.client.post(reverse("nail_service:customer-create"), data=form_data)
        test_user = get_user_model().objects.get(
            username=form_data["username"])

        self.assertEqual(test_user.first_name, form_data["first_name"])
        self.assertEqual(test_user.last_name, form_data["last_name"])
        self.assertEqual(test_user.role, form_data["role"])

    def test_customer_list_search_by_username(self):
        url = CUSTOMER_LIST_URL
        response = self.client.get(url, {"username": "Test_name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["customer_list"]),
            list(get_user_model().objects.filter(username="Test_name"))
        )
