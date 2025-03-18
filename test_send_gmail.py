#!/usr/bin/env python
"""
A test script to verify that the Gmail email configuration in Django settings is working correctly.
This script can be run independently of Django to isolate email configuration issues.
"""

import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'khcc.ioc2025@gmail.com'
EMAIL_HOST_PASSWORD = 'KHCC.123456'  # Replace with your app password

def test_gmail_connection():
    """Test connection to Gmail SMTP server without sending an email"""
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        
        # Start TLS encryption
        server.starttls()
        server.ehlo()
        
        # Login to the server
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Close the connection
        server.quit()
        
        print("✅ Successfully connected to Gmail SMTP server")
        return True
    except Exception as e:
        print(f"❌ Connection to Gmail failed: {e}")
        return False

def send_test_email(recipient_email):
    """Send a test email to verify the entire email sending process"""
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = recipient_email
        msg['Subject'] = f"KHCC-IOC Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Message body
        body = """
        This is a test email sent from the KHCC-IOC Conference system.
        
        If you're receiving this email, it means the email configuration is working correctly.
        
        This is an automated message, please do not reply.
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_HOST_USER, recipient_email, text)
        
        # Close connection
        server.quit()
        
        print(f"✅ Test email successfully sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def django_send_email_test(recipient_email):
    """Test sending email using Django's email functionality"""
    try:
        # Import Django modules
        import os
        import django
        
        # Set up Django environment
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "khcc_conference.settings")
        django.setup()
        
        # Now we can import Django's email module
        from django.core.mail import send_mail
        
        # Send email using Django
        subject = f"Django Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        message = "This is a test email sent using Django's email functionality."
        from_email = EMAIL_HOST_USER
        recipient_list = [recipient_email]
        
        result = send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        
        if result == 1:
            print(f"✅ Django test email successfully sent to {recipient_email}")
            return True
        else:
            print("❌ Django email was not sent")
            return False
    except ImportError:
        print("❌ Could not import Django modules. Make sure you're running this from your Django project directory.")
        return False
    except Exception as e:
        print(f"❌ Django email test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("KHCC-IOC Gmail Configuration Test")
    print("=" * 50)
    
    # Test connection first
    if test_gmail_connection():
        print("\nConnection successful! Testing email sending...")
        
        if len(sys.argv) > 1:
            recipient = sys.argv[1]
        else:
            recipient = input("\nEnter an email address to receive the test email: ")
        
        # Send test email using direct SMTP
        print("\n1. Testing direct SMTP email sending:")
        send_test_email(recipient)
        
        # Send test email using Django
        print("\n2. Testing Django email functionality:")
        django_send_email_test(recipient)
    
    print("\n" + "=" * 50)
    print("IMPORTANT: If the test failed, please check the following:")
    print("1. Verify that you've enabled 'Less secure apps' in your Google account")
    print("2. Generate an 'App Password' if you have 2-Step Verification enabled")
    print("3. Check your internet connection")
    print("4. Make sure your email and password are correct")
    print("=" * 50)