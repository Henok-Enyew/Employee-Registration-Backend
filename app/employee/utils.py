from django.conf import settings
from django.core.mail import send_mail
import pyotp
from datetime import datetime, timedelta
from django.template.loader import render_to_string

def send_verification_email(employee):
    verify_url = f"{settings.FRONTEND_URL}/verify-email/{employee.username}"
    context = {
        'instance': employee,
        'otp': {'otp_code': employee.otp_secret},
        'verify_url' : verify_url

    }
    email_body = render_to_string('otp_email_template.html', context)
    
    send_mail(
        'Verify Your Email',
        '',
        settings.DEFAULT_FROM_EMAIL,
        [employee.email],
        fail_silently=False,
        html_message=email_body
    )


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)  # 5 minutes validity
    return totp.now()

def verify_otp(otp, user_otp):
    return otp == user_otp