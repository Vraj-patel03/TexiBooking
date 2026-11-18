from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from core.models import AdminAccount


class ForgotPasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testadmin',
            email='test@taxibooking.com',
            password='InitialPassword123!',
            is_staff=True
        )
        self.admin_acc = AdminAccount.objects.create(
            username='testadmin',
            email='test@taxibooking.com',
            password=make_password('InitialPassword123!')
        )

    def test_forgot_password_get(self):
        response = self.client.get('/forgot-password/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stage'], 'email')

    def test_send_otp_success(self):
        response = self.client.post('/forgot-password/', {
            'action': 'send_otp',
            'email': 'test@taxibooking.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stage'], 'otp')
        self.assertIn('reset_otp', self.client.session)

    def test_send_otp_nonexistent_email(self):
        response = self.client.post('/forgot-password/', {
            'action': 'send_otp',
            'email': 'unknown@taxibooking.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stage'], 'email')

    def test_verify_otp_flow(self):
        session = self.client.session
        session['reset_otp'] = make_password('654321')
        session['reset_email'] = 'test@taxibooking.com'
        session['reset_stage'] = 'otp'
        session['otp_attempts'] = 0
        session.save()

        # Wrong OTP
        response = self.client.post('/forgot-password/', {
            'action': 'verify_otp',
            'otp': '111111'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stage'], 'otp')

        # Correct OTP
        response = self.client.post('/forgot-password/', {
            'action': 'verify_otp',
            'otp': '654321'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stage'], 'reset')

    def test_reset_password_flow(self):
        session = self.client.session
        session['reset_otp'] = make_password('654321')
        session['reset_email'] = 'test@taxibooking.com'
        session['reset_stage'] = 'reset'
        session.save()

        response = self.client.post('/forgot-password/', {
            'action': 'reset_password',
            'password': 'BrandNewSecurePassword123!',
            'confirm_password': 'BrandNewSecurePassword123!'
        })
        self.assertRedirects(response, '/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNewSecurePassword123!'))
