from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Speaker, Session, ScheduleItem
from .forms import RegistrationForm

def home(request):
    """View for the conference homepage"""
    # Get first 3 speakers to feature on homepage
    featured_speakers = Speaker.objects.all().order_by('order')[:3]
    # Get first few sessions for preview
    upcoming_sessions = Session.objects.all().order_by('date', 'start_time')[:2]
    
    context = {
        'featured_speakers': featured_speakers,
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'conference/home.html', context)

def speakers(request):
    """View for the speakers page"""
    speakers_list = Speaker.objects.all().order_by('order')
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
        if form.is_valid():
            # Save the form but don't commit yet
            registration = form.save(commit=False)
            # Additional processing if needed
            registration.save()
            
            # Show success message
            messages.success(request, "Thank you for registering for the conference!")
            return redirect(reverse('registration_success'))
    else:
        form = RegistrationForm()
    
    return render(request, 'conference/registration.html', {'form': form})

def registration_success(request):
    """View for successful registration"""
    return render(request, 'conference/registration_success.html')
