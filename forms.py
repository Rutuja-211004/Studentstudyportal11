from django import forms
from django.forms import widgets
from . models import*
from django.contrib.auth.forms import UserCreationForm

 
class NotesForm(forms.ModelForm):
    
    class Meta:
        model = Notes
        fields = ['title','description']
        
class DateInput(forms.DateInput):
    input_type='date'
        
class HomeworkForm(forms.ModelForm):
            
    class Meta:
        model = Homework
        fields = ('subject','title','description','due','is_finished')
        widget={'due':DateInput()}


class DashboardForm(forms.Form):
    text=forms.CharField( max_length=100, label="Enter your search :")
               
class TodoForm(forms.ModelForm):
    class Meta:
        model=ToDo
        fields = ['title','is_finished']
        
class ConversionForm(forms.Form):
    CHOICE=[('length','Length'),('mass','Mass')]
    measurement=forms.ChoiceField(choices=CHOICE,widget=forms.RadioSelect)
 
class conversionLengthForm(forms.Form):
    CHOICE=[('yard','Yard'),('foot','Foot')]
    input=forms.CharField(required=False,label=False,widget=forms.TextInput(
    attrs={'type':'number','placeholder':'Enter the Number'}
    ))
    measure1=forms.CharField(
    label='yard',widget=forms.Select(choices=CHOICE)
  )
    measure2=forms.CharField(
    label='',widget=forms.Select(choices=CHOICE)
      )
    
class conversionMassForm(forms.Form):
    CHOICE=[('pound','Pound'),('kilogram','Kilogram')]
    input=forms.CharField(required=False,label=False,widget=forms.TextInput(
    attrs={'type':'number','placeholder':'Enter the Number'}
    ))
    measure1=forms.CharField(
    label='pound',widget=forms.Select(choices=CHOICE)
  )
    measure2=forms.CharField(
    label='',widget=forms.Select(choices=CHOICE)
      )
       
   
    
class userregistraionForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','password1','password2']
    

