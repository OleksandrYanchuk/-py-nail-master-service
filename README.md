Nail Master Service Project

This project was created to provide a platform for nail masters and customers to connect and schedule nail services. It allows nail masters to create their profiles, list their services and prices, and manage their schedule. Customers can search for nail masters, view their profiles, and book appointments for nail services.
Setup and Local Installation

To set up and run the project locally, follow these steps:

1.  Clone the repository:

git clone <repository_url>

2. Create a virtual environment:

python -m venv venv

3. Activate the virtual environment:

-	  For Windows:

venv\Scripts\activate

-	For macOS and Linux:

    source venv/bin/activate

4. Install the project dependencies:

pip install -r requirements.txt

5. Apply database migrations:

python manage.py migrate

6. Create a superuser to access the admin panel:

python manage.py createsuperuser

7. Start the development server:

python manage.py runserver

8. Open your web browser and go to http://localhost:8000 to access the application.

## Setting up Environment Variables

The Nail Master Service project uses environment variables to store sensitive information and configuration settings. To set up the required environment variables, follow these steps:

1. Rename a file name '.env_sample' to `.env` in the project root directory.

2. Make sure to replace `your_secret_key_value_here` with your actual secret key.

3. Install the `python-dotenv` library by running the following command in your virtual environment:
pip install python-dotenv

Use the following command to load prepared data from fixture to test and debug your code:
python manage.py loaddata nail_master_service_db_data.json
masters: Test_master, Test_master3, Test_master4, Test_master6, Test_master7, Test_master8
customers: test_customer, test_customer2, test_customer3, test_customer4, test_customer5, test_customer6, test_customer8
pass for all users: b8396313


Some Project Files

models.py

The models.py file contains the Django models used in the project. It defines the following models:

•	Services: Represents the nail services offered by the nail masters. It has fields for the service name, price, and time required for the service.

•	User: Extends the built-in Django AbstractUser model and represents the users of the application. It includes a custom Role field to distinguish between admin, customer, and master users.

•	Customer: Represents a customer user. It inherits from the User model and includes additional fields for the customer's selected services and assigned masters.

•	Master: Represents a nail master user. It inherits from the User model and includes additional fields for the master's selected services and assigned customers.

•	Events: Represents events scheduled by the nail masters. It includes fields for the event title, start date, end date, and the corresponding master.

•	PriceList: Represents the price list for a specific master and service. It includes fields for the master, service, price, and time required for the service.

views.py

The views.py file contains the view functions and class-based views used in the Nail Master Service project. It defines the following views:

•	index: This view function renders the home page and displays basic statistics about the application, such as the total number of users and visits.

•	user_details: This view function redirects the user to their respective profile page based on their role (master or customer).

•	master_required: This decorator function restricts access to views only for users with the role of "Master". It checks if the user is authenticated as a master and redirects them to the login page if not.

•	MasterListView: This class-based view lists all the nail masters in the system. It includes a search form that allows users to filter masters by their username.

•	MasterUpdateView: This class-based view allows a master to update their profile and associated services. It includes a form that allows the master to modify their details and update the prices for their services.

•	MasterDetailView: This class-based view displays the detailed profile of a specific nail master. It also shows the events scheduled by that master.

•	MasterCreateView: This class-based view allows the creation of a new nail master profile. It presents a form for the user to enter their information and create their profile.

•	MasterDeleteView: This class-based view allows a master to delete their profile. It confirms the deletion and removes the master from the system.

•	CustomerListView: This class-based view lists all the customers in the system. It includes a search form that enables users to filter customers by their username.

•	CustomerUpdateView: This class-based view allows a customer to update their profile. It presents a form that allows the customer to modify their information.

These views are responsible for handling various user interactions, displaying information, and providing the necessary forms for data input and modification.
 

