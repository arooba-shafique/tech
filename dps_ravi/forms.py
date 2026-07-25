from django import forms
from academics.models import StudentProfile, Class

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'roll_number', 
            'admission_number', 
            'student_class', 
            'section', 
            'date_of_birth', 
            'gender', 
            'phone', 
            'address', 
            'admission_date', 
            'is_active'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }