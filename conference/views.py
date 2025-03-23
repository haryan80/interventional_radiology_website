from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.db import transaction
import logging

from .models import Speaker, Session, ScheduleItem, Registration
from .forms import RegistrationForm

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    """View for the conference homepage"""
    # Get first 3 visible speakers to feature on homepage
    featured_speakers = Speaker.objects.filter(is_visible=True).order_by('order')[:3]
    # Get first few sessions for preview
    upcoming_sessions = Session.objects.all().order_by('date', 'start_time')[:2]
    
    context = {
        'featured_speakers': featured_speakers,
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'conference/home.html', context)

def speakers(request):
    """View for the speakers page"""
    speakers_list = Speaker.objects.filter(is_visible=True).order_by('order')
    return render(request, 'conference/speakers.html', {'speakers': speakers_list})

def schedule(request):
    """View for the conference schedule page"""
    sessions = Session.objects.all().order_by('date', 'start_time')
    
    # Group sessions by date for easier template rendering
    schedule_by_date = {}
    for session in sessions:
        date_str = session.date.strftime('%Y-%m-%d')
        if date_str not in schedule_by_date:
            schedule_by_date[date_str] = {
                'date_display': session.date.strftime('%A, %B %d, %Y'),
                'sessions': []
            }
        schedule_by_date[date_str]['sessions'].append(session)
    
    return render(request, 'conference/schedule.html', {'schedule_by_date': schedule_by_date})

def registration(request):
    """View for the registration page"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        print(f"Form data received: {request.POST}")  # Basic console logging
        
        if form.is_valid():
            print(f"Form is valid. Cleaned data: {form.cleaned_data}")
            
            try:
                # Use a transaction to ensure data integrity
                with transaction.atomic():
                    # Save the form but don't commit yet
                    registration = form.save(commit=False)
                    print(f"Registration object created (not saved yet): {registration.full_name}, {registration.email}")
                    
                    # Force debug output to console
                    print(f"About to save registration to database for: {registration.full_name}")
                    
                    # Save to database - THIS IS THE CRITICAL STEP
                    registration.save()
                    print(f"Registration saved with ID: {registration.id}")
                    
                    # Double-check the save by querying the database
                    try:
                        # Query by ID which is the most reliable
                        verify_reg = Registration.objects.get(id=registration.id)
                        print(f"VERIFICATION: Found registration in database with ID {verify_reg.id}, name: {verify_reg.full_name}")
                    except Registration.DoesNotExist:
                        print("ERROR: Registration was not found in database after save!")
                    
                    # Send confirmation email to applicant
                    send_mail(
                        'KHCC IOC 2025 Conference Registration Confirmation',
                        f'''Dear {registration.full_name},

Thank you for registering for the KHCC International Oncology Conference 2025. Your registration has been successfully processed and we're delighted you'll be joining us.

Registration Details:
- Name: {registration.full_name}
- Email: {registration.email}
- Institution: {registration.institution}
- Country: {registration.country}
- Attendee Type: {registration.get_attendee_type_display()}

What's Next:
- You will receive additional information about the conference schedule closer to the event date
- If you have any questions, please contact us at khcc.ioc2025@gmail.com

We look forward to seeing you at the conference!

Warm regards,
The KHCC IOC 2025 Conference Team''',
                        'noreply@example.com',  # From email
                        [registration.email],  # To email
                        fail_silently=False,
                    )
                    
                    # Send notification email to admin
                    send_mail(
                        'New KHCC IOC 2025 Conference Registration',
                        f'''A new registration has been submitted for the KHCC IOC 2025 Conference.

Registration Details:
- Name: {registration.full_name}
- Email: {registration.email}
- Phone: {registration.phone or "Not provided"}
- Institution: {registration.institution}
- Country: {registration.country}
- Attendee Type: {registration.get_attendee_type_display()}
- Special Requirements: {registration.special_requirements or "None"}
- Submitted on: {registration.created_at.strftime("%Y-%m-%d %H:%M")}

Please review this registration in the admin panel.''',
                        'noreply@example.com',  # From email
                        ['khcc.ioc2025@gmail.com'],  # Admin email
                        fail_silently=False,
                    )
                
                print("Transaction completed successfully")
                messages.success(request, "Thank you for registering for the conference!")
                return redirect(reverse('registration_success'))
            
            except Exception as e:
                # Log any errors with detailed traceback
                import traceback
                print(f"ERROR saving registration: {str(e)}")
                print(traceback.format_exc())
                messages.error(request, "An error occurred during registration. Please try again.")
        else:
            # Log form validation errors
            print(f"Form validation errors: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = RegistrationForm()
    
    return render(request, 'conference/registration.html', {'form': form})

def registration_success(request):
    """View for successful registration"""
    return render(request, 'conference/registration_success.html')
