from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    """Form for conference registration"""
    # Add a confirmation field that's not in the model
    email_confirm = forms.EmailField(label="Confirm Email")
    
    class Meta:
        model = Registration
        fields = ['full_name', 'email', 'email_confirm', 'phone', 'institution', 
                  'attendee_type', 'special_requirements']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 
                                               'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 
                                           'placeholder': 'Enter your email address'}),
            'email_confirm': forms.EmailInput(attrs={'class': 'form-control', 
                                                   'placeholder': 'Confirm your email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 
                                          'placeholder': 'Enter your phone number'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 
                                                'placeholder': 'Enter your institution/hospital'}),
            'attendee_type': forms.Select(attrs={'class': 'form-select'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 
                                                        'placeholder': 'Enter any special requirements or dietary restrictions',
                                                        'rows': 3}),
        }
    
    def clean(self):
        """Validate that email and email_confirm match"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email_confirm = cleaned_data.get('email_confirm')
        
        if email and email_confirm and email != email_confirm:
            self.add_error('email_confirm', "Email addresses do not match")
        
        return cleaned_data 