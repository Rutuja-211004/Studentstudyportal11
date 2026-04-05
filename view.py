from django import contrib
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.checks import messages
from django.forms.widgets import FileInput
from django.shortcuts import*
from django.contrib.auth import*
from .models import  *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
from django.http import HttpResponse


from . forms import*
import wikipedia
import requests
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')
@login_required
def notes(request):
    if request.method=="POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes=Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes added from {request.user.username}successfully")
    else:
        form=NotesForm()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)
@login_required
def delete_note(request,pk=None):
    
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailview(generic.DetailView):
    model=Notes
    
@login_required


def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            # Safely check if 'is_finished' is set in the POST request
            finished = request.POST.get('is_finished') == 'on'
            
            # Parsing due date properly
            due_date = form.cleaned_data['due']  # Assuming the form is handling this
            
            # Creating homework instance with form data
            homework = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],  # Fix typo here
                due=due_date,
                is_finished=finished
            )
            homework.save()
            messages.success(request, f'Homework Added by {request.user.username}!')
        else:
            # Handle invalid form (optional)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = HomeworkForm()

    # Fetching homeworks assigned to the user
    homeworks = Homework.objects.filter(user=request.user)
    
    # Checking if all homeworks are finished
    homework_done = all(hw.is_finished for hw in homeworks)  # Homework is done if all are finished

    context = {
        'homeworks': homeworks,
        'homeworks_done': homework_done,
        'form': form
    }
    return render(request, 'dashboard/homework.html', context)
@login_required
def update_homework(request, pk=None):
    
    homework = get_object_or_404(Homework, id=pk)

    homework.is_finished = not homework.is_finished
    homework.save()
    messages.success(request, f'Homework "{homework.title}" updated successfully!')
    
    return redirect('homework')
@login_required    
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def logout_view(request):
    logout(request)
    return render(request,"dashboard/logout.html")
 # Redirect to the login page or wherever you prefer


def youtube(request):
    if request.method=="POST":
        form = DashboardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=10)
        result_list=[]
        for i in video.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc=''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc +=j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context={
                        'form':form,
                        'results':result_list
                    }

        return render(request,"dashboard/youtube.html",context)
    else:
        form=DashboardForm()
    context={'form':form}
    return render(request,"dashboard/youtube.html",context)

@login_required
def todo(request):
    if request.method=="POST":
        form=TodoForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST["is_finished"]
                if finished =='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            todos = ToDo(
                    user=request.user,
                    title=request.POST['title'],
                    is_finished=finished,
                )
            todos.save()
            messages.success(request,f"Todo Added from {request.user.username}!!")
    else:
        form= TodoForm()
    todo=ToDo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done=True
    else:
        todos_done=False
    context={
                'form':form,
                'todos':todo,
                'todos_done':todos_done
            }
    return render(request,"dashboard/todo.html",context)

@login_required
def update_todo(request,pk=None):
    todo=ToDo.object.get(id=pk)
    if todo.is_finished==True:
        todo.is_finished=False 
    else:
        todo.is_finished=True
    todo.save()
    return redirect('todo')
@login_required
def delete_todo(request,pk=None):
        ToDo.objects.get(id=pk).delete()
        return redirect("todo")

@login_required  
def book(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = request.POST['text']
            url = "https://www.googleapis.com/books/v1/volumes?q=" + text
            try:
                r = requests.get(url)
                r.raise_for_status()  # This will raise an error for 4xx/5xx responses
                answer = r.json()

                result_list = []

                # Check if 'items' exists in the response
                if 'items' in answer:
                    for item in answer['items']:
                        volume_info = item.get('volumeInfo', {})

                        result_dict = {
                            'title': volume_info.get('title', 'No title available'),
                            'subtitle': volume_info.get('subtitle'),
                            'description': volume_info.get('description'),
                            'count': volume_info.get('pageCount'),
                            'categories': volume_info.get('categories'),
                            'rating': volume_info.get('averageRating'),
                            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail'),
                            'preview': volume_info.get('previewLink')
                        }

                        result_list.append(result_dict)

                    context = {
                        'form': form,
                        'results': result_list
                    }
                else:
                    # Handle the case where no items are found
                    context = {
                        'form': form,
                        'results': [],
                        'error': 'No results found for the search term.'
                    }
            except requests.exceptions.RequestException as e:
                # Handle request-related errors
                context = {
                    'form': form,
                    'error': f'Error fetching data from Google Books API: {str(e)}'
                }
            except ValueError:
                # Handle JSON decoding errors
                context = {
                    'form': form,
                    'error': 'Error parsing the response from the API.'
                }
        else:
            # Handle form validation errors
            context = {
                'form': form,
                'error': 'Invalid form submission.'
            }

        return render(request, 'dashboard/books.html', context)
    
    else:
        form = DashboardForm()

    context = {'form': form}
    return render(request, "dashboard/books.html", context)

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + text
        r = requests.get(url)
        try:
            answer = r.json()
            # Extract phonetics, audio, definitions, examples, and synonyms
            phonetics = answer[0]['phonetics'][0].get('text', '')
            audio = answer[0]['phonetics'][0].get('audio', '')
            definitions = answer[0]['meanings'][0].get('definitions', [])
            # Default empty lists if there are no definitions
            definition = definitions[0].get('definition', '') if definitions else ''
            example = definitions[0].get('example', '') if definitions and 'example' in definitions[0] else ''
            synonyms = definitions[0].get('synonyms', [])

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except (IndexError, KeyError) as e:
            # Handle errors when data is missing or malformed
            context = {
                'form': form,
                'input': text,
                'error': 'Could not find the word or its details. Please try again.'
            }
        return render(request, "dashboard/dictionary.html", context)
    
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, "dashboard/dictionary.html", context)

def wiki(request):
    if request.method=="POST":
        text=request.POST['text']
        form=DashboardForm(request.POST)
        search=wikipedia.page(text)
        context= {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,"dashboard/wiki.html",context)
    else:
        form=DashboardForm()
        context={
            'form':form
        }
    return render(request,"dashboard/wiki.html",context)
def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        measurement = request.POST.get('measurement')
        answer = ''

        # Length Conversion
        if measurement == 'length':
            measurement_form = conversionLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                try:
                    input_value = float(input_value)
                    if input_value >= 0:
                        if first == 'yard' and second == 'foot':
                            answer = f'{input_value} yard = {input_value * 3} foot'
                        elif first == 'foot' and second == 'yard':
                            answer = f'{input_value} foot = {input_value / 3} yard'
                except ValueError:
                    answer = "Please enter a valid number."
                context.update({
                    'answer': answer
                })

        # Mass Conversion
        elif measurement == 'mass':
            measurement_form = conversionMassForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                try:
                    input_value = float(input_value)
                    if input_value >= 0:
                        if first == 'pound' and second == 'kilogram':
                            answer = f'{input_value} pound = {input_value * 0.453592} kilogram'
                        elif first == 'kilogram' and second == 'pound':
                            answer = f'{input_value} kilogram = {input_value * 2.20462} pound'
                except ValueError:
                    answer = "Please enter a valid number."
                context.update({
                    'answer': answer
                })

        return render(request, "dashboard/conversion.html", context)

    else:
        form = ConversionForm()
        context = {
            'form': form,
            'input': False
        }
        return render(request, "dashboard/conversion.html", context)

def register(request): 
    
    if request.method=='POST':
        form=userregistraionForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"Acoount Created for {username}!!")
            return redirect("login")
    else:
        form=userregistraionForm()
    context={
        'form':form
  } 
    return render(request,"dashboard/register.html",context)

@login_required      
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=ToDo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos) == 0:
        todos_done = True 
    else:
        todos_done = False
    context={
           'homework':homeworks,
           'todos': todos,
           'homework_done': homework_done,
           'todos_done': todos_done
       }
      
    return render(request,"dashboard/profile.html",context)

        
        
    

    
