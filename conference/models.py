from django.db import models
import uuid
import os

# Function to generate unique filenames for uploaded images
def get_unique_filename(instance, filename):
    """Generate a unique filename for uploaded images to prevent collisions"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('speakers', filename)

class Speaker(models.Model):
    """Model representing a conference speaker"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField()
    photo = models.ImageField(upload_to=get_unique_filename, blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order on the speakers page")
    is_visible = models.BooleanField(default=True, help_text="Whether to display this speaker on the website")
    
    def __str__(self):
        return self.name

class Session(models.Model):
    """Model representing a conference session"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.name} - {self.date}"

class ScheduleItem(models.Model):
    """Model representing an item in the conference schedule"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    speakers = models.ManyToManyField(Speaker, blank=True, related_name='schedule_items')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False, help_text="Whether this is a break, lunch, etc.")
    
    class Meta:
        ordering = ['session__date', 'start_time']
    
    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"

class Registration(models.Model):
    """Model for conference registrations"""
    ATTENDEE_TYPES = (
        ('specialist', 'Specialist'),
        ('trainee', 'Trainee/Fellow'),
    )
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    institution = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    attendee_type = models.CharField(max_length=20, choices=ATTENDEE_TYPES)
    special_requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.full_name} - {self.attendee_type}"
        
    class Meta:
        ordering = ['-created_at']
