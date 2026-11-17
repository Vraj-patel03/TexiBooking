# Taxi Booking System

A Django-based admin authentication starter project with an admin dashboard, restricted admin registration, and an email-OTP password reset flow.

## Features

- Admin login using Django authentication
- Staff-only dashboard access
- Superuser-only admin registration
- Forgot-password flow on one page (email → OTP → new password)
- Six-digit OTP generated with Python `secrets`
- Hashed OTP stored in the Django session
- Maximum of five incorrect OTP attempts
- Django password validation during password reset
- SQLite database for local development
- Console email backend (OTP email is printed in the runserver terminal)

## Requirements

- Python 3.12 or newer
- pip

## Setup (Windows PowerShell)

1. Open this project folder in VS Code.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a local secret key for your development session and set it in PowerShell:

   ```powershell
   $env:DJANGO_SECRET_KEY = 'replace-this-with-a-long-random-secret'
   ```

5. Apply migrations:

   ```powershell
   python manage.py migrate
   ```

6. Create the first superuser:

   ```powershell
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```powershell
   python manage.py runserver
   ```

8. Open `http://127.0.0.1:8000/` in your browser. The OTP email content appears in the terminal because the project uses Django's console email backend.

## GitHub upload

Create an empty repository on GitHub. In this project folder, run:

```powershell
git init
git add .
git commit -m "Initial Taxi Booking System project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own GitHub repository URL.

## Important security notes

- This is a development project, not production-ready deployment configuration.
- Do not commit `venv/`, `db.sqlite3`, `.env`, passwords, or secret keys. The included `.gitignore` excludes these local files.
- Set `DJANGO_SECRET_KEY` through your environment before running the project.
- `DEBUG` is enabled for local development. Turn it off and configure `ALLOWED_HOSTS`, HTTPS, secure cookies, and production email settings before deployment.
- The current console email backend is for development/testing only. Configure a real email provider for deployment.
