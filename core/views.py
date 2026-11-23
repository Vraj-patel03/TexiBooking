import secrets
# pyrefly: ignore[missing-import]
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .models import AdminAccount, Customer, Driver
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q



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

    drivers_count = Driver.objects.count()

    return render(request, 'core/dashboard.html', {
        'drivers_count': drivers_count,
    })



@user_passes_test(
    lambda user: user.is_authenticated and user.is_active and user.is_superuser,
    login_url='login'
)
def register_view(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')

        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')

        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')

        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already exists.')

        elif AdminAccount.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Admin account already exists.')

        else:
            try:
                validate_password(password)

            except ValidationError as errors:
                for error in errors:
                    messages.error(request, error)

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

                messages.success(
                    request,
                    'Admin registered successfully.'
                )
                return redirect('login')

    # IMPORTANT: This return must be outside the POST condition.
    return render(request, 'core/register.html')


def forgot_password(request):
    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'send_otp':
            email = request.POST.get('email', '').strip()

            # Clear any previous reset attempt
            for key in [
                'reset_otp',
                'reset_email',
                'reset_stage',
                'otp_attempts'
            ]:
                request.session.pop(key, None)

            # Search Django User, not only AdminAccount
            user = User.objects.filter(
                email__iexact=email,
                is_staff=True,
                is_active=True
            ).first()

            if not user:
                messages.error(request, 'Admin email not found.')

            else:
                otp = secrets.randbelow(900000) + 100000

                try:
                    send_mail(
                        'Taxi Booking System - Password Reset OTP',
                        f'Your password reset OTP is: {otp}',
                        'admin@taxibooking.com',
                        [user.email],
                        fail_silently=False,
                    )

                    request.session['reset_otp'] = make_password(str(otp))
                    request.session['reset_email'] = user.email
                    request.session['reset_stage'] = 'otp'
                    request.session['otp_attempts'] = 0
                    request.session.set_expiry(300)

                    messages.success(
                        request,
                        'OTP generated successfully. Check the terminal.'
                    )

                except Exception:
                    messages.error(
                        request,
                        'Unable to generate OTP. Please try again.'
                    )

        elif action == 'verify_otp':

            if (
                request.session.get('reset_stage') != 'otp'
                or not request.session.get('reset_otp')
                or not request.session.get('reset_email')
            ):
                messages.error(
                    request,
                    'Please request a new OTP.'
                )
                return redirect('forgot_password')

            entered_otp = request.POST.get('otp', '').strip()
            attempts = request.session.get('otp_attempts', 0)

            if attempts >= 5:
                request.session.flush()
                messages.error(
                    request,
                    'Too many attempts. Please request a new OTP.'
                )
                return redirect('forgot_password')

            if (
                len(entered_otp) == 6
                and entered_otp.isdigit()
                and check_password(
                    entered_otp,
                    request.session.get('reset_otp')
                )
            ):
                request.session['reset_stage'] = 'reset'
                request.session.pop('otp_attempts', None)

                messages.success(
                    request,
                    'OTP verified successfully.'
                )

            else:
                attempts += 1
                request.session['otp_attempts'] = attempts

                if attempts >= 5:
                    for key in [
                        'reset_otp',
                        'reset_email',
                        'reset_stage',
                        'otp_attempts'
                    ]:
                        request.session.pop(key, None)

                    messages.error(
                        request,
                        'Too many incorrect attempts. Request a new OTP.'
                    )
                    return redirect('forgot_password')

                messages.error(
                    request,
                    f'Incorrect OTP. {5 - attempts} attempts remaining.'
                )

        elif action == 'reset_password':

            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if (
                request.session.get('reset_stage') != 'reset'
                or not request.session.get('reset_email')
            ):
                messages.error(
                    request,
                    'Please verify your OTP first.'
                )
                return redirect('forgot_password')

            elif not password or password != confirm_password:
                messages.error(
                    request,
                    'Passwords do not match or are empty.'
                )

            else:
                email = request.session.get('reset_email')

                user = User.objects.filter(
                    email__iexact=email,
                    is_staff=True,
                    is_active=True
                ).first()

                if not user:
                    messages.error(
                        request,
                        'Admin account not found.'
                    )

                else:
                    try:
                        validate_password(password, user)

                    except ValidationError as errors:
                        for error in errors:
                            messages.error(request, error)

                    else:
                        user.set_password(password)
                        user.save()

                        # Update custom account if it exists
                        admin = AdminAccount.objects.filter(
                            username=user.username
                        ).first()

                        if admin:
                            admin.password = make_password(password)
                            admin.save()

                        for key in [
                            'reset_otp',
                            'reset_email',
                            'reset_stage',
                            'otp_attempts'
                        ]:
                            request.session.pop(key, None)

                        messages.success(
                            request,
                            'Password reset successfully. Please log in.'
                        )
                        return redirect('login')

    stage = request.session.get('reset_stage', 'email')

    return render(request, 'core/forgot_password.html', {
        'stage': stage,
        'email': request.session.get('reset_email', ''),
    })



# Allow only logged-in staff members
admin_required = user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url='login'
)


@login_required(login_url='login')
@admin_required
def drivers_view(request):
    drivers = Driver.objects.all().order_by('-created_at')

    return render(request, 'core/drivers.html', {
        'drivers': drivers
    })

@login_required(login_url='login')
@admin_required
def user_create(request):

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')

        if not name or not email or not mobile or not password:
            messages.error(request, 'All fields are required.')

        elif Customer.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already exists.')

        else:
            customer = Customer(
                name=name,
                email=email,
                mobile=mobile
            )

            customer.set_password(password)
            customer.save()

            messages.success(request, 'Customer added successfully.')
            return redirect('users')

    return render(request, 'core/user_create.html')


@login_required(login_url='login')
@admin_required
def user_edit(request, user_id):
    customer = get_object_or_404(Customer, id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')

        if not name or not email or not mobile:
            messages.error(request, 'All fields are required.')

        elif Customer.objects.filter(email__iexact=email).exclude(id=user_id).exists():
            messages.error(request, 'Email already exists.')

        else:
            customer.name = name
            customer.email = email
            customer.mobile = mobile

            if password:
                customer.set_password(password)

            customer.save()

            messages.success(request, 'Customer updated successfully.')
            return redirect('users')

    return render(request, 'core/user_edit.html', {
        'customer': customer
    })


@login_required(login_url='login')
@admin_required
def user_delete(request, user_id):
    customer = get_object_or_404(Customer, id=user_id)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')

    return redirect('users')


@login_required(login_url='login')
@admin_required
def users_view(request):

    search_query = request.GET.get('search', '').strip()

    customers = Customer.objects.all()

    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    customers = customers.order_by('-created_at')

    return render(request, 'core/users.html', {
        'customers': customers,
        'search_query': search_query
    })


@login_required(login_url='login')
@admin_required
def user_detail(request, user_id):
    customer = get_object_or_404(Customer, id=user_id)

    return render(request, 'core/user_detail.html', {
        'customer': customer
    })


@login_required(login_url='login')
@admin_required
def bookings_view(request):
    return render(request, 'core/bookings.html', {
        'page_title': 'Bookings',
        'page_description': 'View and manage taxi booking records.'
    })