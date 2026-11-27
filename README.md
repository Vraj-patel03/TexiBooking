# Taxi Booking System

A web-based Taxi Booking System built with **Python, Django, Bootstrap,
and SQLite**. The project includes separate admin and customer
workflows, customer registration and authentication, and management
pages for customers and drivers.

## Features

### Admin Panel

-   Admin login and logout.
-   Staff-only access to the admin dashboard and management pages.
-   Admin registration flow with restricted access.
-   Forgot-password flow using email and a six-digit OTP.
-   OTP stored as a hash in the Django session.
-   Maximum of five incorrect OTP attempts.
-   Password reset with Django password validation.

### Customer Features

-   Public customer registration.
-   Registration fields: name, email, password, and phone number.
-   Required-field, duplicate-email, and minimum password-length checks.
-   Customer passwords stored using Django password hashing.
-   Customer login using email and password.
-   Session-based customer authentication.
-   Separate customer dashboard showing account information.
-   Customer logout.

### Management Features

-   Customer listing and customer search by name or email.
-   Customer profile, create, edit, and delete pages.
-   Driver listing and driver search by name or email.
-   Driver profile page with personal information.
-   Driver deletion.
-   Driver list displayed on the admin dashboard.
-   Booking history section in the driver profile currently displays an
    empty-state message when no booking records are available.

### Technology

-   Python
-   Django
-   SQLite
-   Bootstrap
-   HTML and CSS

## Project Structure

``` text
TaxiBookingSystem/
├── config/
│   ├── settings.py
│   └── urls.py
├── core/
│   ├── migrations/
│   ├── templates/
│   │   └── core/
│   ├── admin.py
│   ├── models.py
│   └── views.py
├── manage.py
├── requirements.txt
└── README.md
```

## Requirements

-   Python 3.12 or newer
-   pip

## Setup on Windows (PowerShell)

1.  Clone the repository:

    ``` powershell
    git clone https://github.com/Vraj-patel03/TexiBooking.git
    cd TexiBooking
    ```

2.  Create and activate a virtual environment:

    ``` powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

3.  Install project dependencies:

    ``` powershell
    pip install -r requirements.txt
    ```

4.  Set a development secret key in the current PowerShell session:

    ``` powershell
    $env:DJANGO_SECRET_KEY = 'replace-this-with-a-long-random-secret'
    ```

5.  Apply database migrations:

    ``` powershell
    python manage.py migrate
    ```

6.  Create a Django superuser if required by the admin setup:

    ``` powershell
    python manage.py createsuperuser
    ```

7.  Start the development server:

    ``` powershell
    python manage.py runserver
    ```

8.  Open the application:

    -   Admin login: `http://127.0.0.1:8000/`
    -   Customer registration:
        `http://127.0.0.1:8000/customer-register/`
    -   Customer login: `http://127.0.0.1:8000/customer-login/`

The forgot-password flow currently uses the Django console email backend
in development, so OTP email content is printed in the runserver
terminal.

## Run Tests

Run Django's system checks:

``` powershell
python manage.py check
```

Run the project's tests:

``` powershell
python manage.py test
```

## GitHub

Repository: <https://github.com/Vraj-patel03/TexiBooking>

To commit and push local changes:

``` powershell
git add .
git commit -m "Describe your changes"
git push origin main
```

## Security and Development Notes

-   This project is intended for local development and learning; it is
    not a production-ready deployment configuration.
-   Do not commit `venv/`, `db.sqlite3`, `.env` files, passwords, or
    secret keys.
-   Keep `DJANGO_SECRET_KEY` outside source control and use a strong
    secret value.
-   Before deployment, disable `DEBUG`, configure `ALLOWED_HOSTS`,
    HTTPS, secure cookies, and production email settings.
-   The console email backend is suitable for local testing only.
    Configure a real email provider before deployment.
-   Customer login uses a separate customer session key and does not
    replace the existing admin authentication flow.
-   Booking history is currently a placeholder; this README does not
    claim that a complete booking workflow is implemented.
