from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import send_mail

def send_verification_email(employee):
    token = str(RefreshToken.for_user(employee).access_token)
    verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"
    
    send_mail(
        'Verify Your Email',
        f'Click to verify: {verify_url}',
        settings.DEFAULT_FROM_EMAIL,
        [employee.email],
        fail_silently=False,
    )