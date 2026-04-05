from django.db import models 
from django.contrib.auth.models import User

class Notes(models.Model):
     user=models.ForeignKey(User,on_delete=models.CASCADE) 
     title=models.CharField(max_length=200)
     description=models.TextField()
     
     def __str__(self):
          return self.title

     class Meta:
          verbose_name="note"
          verbose_name_plural="notes"
 
class Homework(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField() 
    due = models.DateTimeField()  # Changed to DateTimeField to include both date and time
    is_finished = models.BooleanField(default=False)
    completed_on = models.DateField(null=True, blank=True)  # Optional field to track when homework is completed

    def __str__(self):     
        return self.title


class ToDo(models.Model):
     user=models.ForeignKey(User,on_delete=models.CASCADE)
     title=models.CharField(max_length=100)
     is_finished=models.BooleanField(default=False)
     def __str__(self):
          return self.title
