import secrets
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .models import AdminAccount
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('login')


def dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')

    return render(request, 'core/dashboard.html')


@user_passes_test(
    lambda user: user.is_authenticated and user.is_active and user.is_superuser,
    login_url='login'
)
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True
            )

            AdminAccount.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )

            messages.success(request, 'Admin registered successfully.')
            return redirect('login')

    return render(request, 'core/register.html')

def forgot_password(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_otp':
            email = request.POST.get('email')
            admin = AdminAccount.objects.filter(email=email).first()

            if admin:
                otp = secrets.randbelow(900000) + 100000
                
                request.session['reset_otp'] = make_password(str(otp))
                request.session['reset_email'] = email
                request.session['reset_stage'] = 'otp'
                request.session['otp_attempts'] = 0
                request.session.set_expiry(300)

                send_mail(
                    'Taxi Booking System - Password Reset OTP',
                    f'Your password reset OTP is: {otp}',
                    'admin@taxibooking.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'OTP sent successfully. Check your terminal.')
            else:
                messages.error(request, 'Admin email not found.')

        elif action == 'verify_otp':
            entered_otp = request.POST.get('otp')
            attempts = request.session.get('otp_attempts', 0)

            if attempts >= 5:
                request.session.pop('reset_otp', None)
                request.session.pop('reset_email', None)
                request.session.pop('reset_stage', None)
                request.session.pop('otp_attempts', None)

                messages.error(request, 'Too many incorrect attempts. Please request a new OTP.')
                return redirect('forgot_password')

            if entered_otp and check_password(entered_otp,
                request.session.get('reset_otp', '')
            ):
                request.session['reset_stage'] = 'reset'
                request.session.pop('otp_attempts', None)

                messages.success(request, 'OTP verified successfully.')

            else:
                attempts += 1
                request.session['otp_attempts'] = attempts

                if attempts >= 5:
                    request.session.pop('reset_otp', None)
                    request.session.pop('reset_email', None)
                    request.session.pop('reset_stage', None)
                    request.session.pop('otp_attempts', None)

                    messages.error(request, 'Too many incorrect attempts. Please request a new OTP.')
                    return redirect('forgot_password')

                messages.error(
                    request,
                    f'Incorrect OTP. {5 - attempts} attempts remaining.'
                )            
        elif action == 'reset_password':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if request.session.get('reset_stage') != 'reset':
                messages.error(request, 'Please verify your OTP first.')

            elif password != confirm_password:
                messages.error(request, 'Passwords do not match.')

            else:
                email = request.session.get('reset_email')
                admin = AdminAccount.objects.filter(email=email).first()

                if admin:
                    user = User.objects.filter(username=admin.username).first()

                    if user:
                        try:
                            validate_password(password, user)
                        except ValidationError as errors:
                            for error in errors:
                                messages.error(request, error)
                        else:
                            user.set_password(password)
                            user.save()

                            admin.password = make_password(password)
                            admin.save()

                            for key in ['reset_otp', 'reset_email', 'reset_stage', 'otp_attempts']:
                                request.session.pop(key, None)

                            messages.success(request, 'Password reset successfully.')
                            return redirect('login')
                    else:
                        messages.error(request, 'Admin account not found.')
                else:
                    messages.error(request, 'Admin account not found.')

    return render(request, 'core/forgot_password.html', {
        'stage': request.session.get('reset_stage', 'email'),
        'email': request.session.get('reset_email', ''),
    })