from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import *
from django.templatetags.static import static
import mimetypes
import re
import requests, json
from ai.read_file import extract_from_word, extract_text_from_pdf, summarize, tag, extract_excel_data  # Import your extraction functions
# Define the MIME type to friendly name mapping
MIME_TYPE_MAPPING = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
    'application/vnd.ms-excel': 'excel'
    # Add other mappings as needed
}

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"Attempting login for email: {email}")  # Debugging

        try:
            user = Techie.objects.get(email=email)
            print(f"User found: {user}")  # Debugging
        except Techie.DoesNotExist:
            messages.error(request, 'User does not exist')
            return redirect('login')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            print("User authenticated")  # Debugging
            login(request, user)
            return redirect('home')
        else:
            print("Authentication failed")  # Debugging
            messages.error(request, 'Invalid login credentials')

    context = {'page': page}
    return render(request, 'pages/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration!')
    return render(request, 'pages/login_register.html', {'form': form})

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    image_url = ''
    docs = File.objects.filter(
        Q(host=request.user) &
        (Q(fname__icontains=q) | 
        Q(file_text__icontains=q) | 
        Q(file_type__icontains=q) | 
        Q(file_tags__icontains=q) | 
        Q(file_summary__icontains=q))
    )
    docs = docs[:5]
    for doc in docs:
        doc.file_summary = re.sub(r'\*\*', '', doc.file_summary)
        docs.file_summary = re.sub(r'\*', '', doc.file_summary)
        doc.file_size = round(doc.file_size / (1024 * 1024), 2)
        image_url = static(f'images/{doc.file_type}.png')


    total_storage = sum(doc.file_size for doc in docs)


    chat = Dialogue.objects.filter(
    Q(host=request.user) &
    (Q(query__icontains=q) | Q(answer__icontains=q))
)
    for query in chat:
        query.answer = re.sub(r'\*\*', '', query.answer)
        query.answer = re.sub(r'\*', '', query.answer)
        query.answer = query.answer[:50] + '...'
    context = {'docs': docs, 'chats':chat, 'storage': total_storage, 'chats_count': chat.count(), 'docs_count': docs.count(), 'image_url': image_url}
    return render(request, 'pages/home.html', context)

@login_required(login_url='login')
def upload_file(request):
    user_files = File.objects.filter(host=request.user)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.file_size = file_instance.file_content.size

            # Determine the file type
            mime_type, _ = mimetypes.guess_type(file_instance.file_content.name)
            file_instance.file_type = MIME_TYPE_MAPPING.get(mime_type, 'Unknown file type')

            # Extract text from the file based on its type
            if file_instance.file_type == 'docx':
                file_instance.file_text = extract_from_word(file_instance.file_content)
            elif file_instance.file_type == 'pdf':
                file_instance.file_text = extract_text_from_pdf(file_instance.file_content)
            else:
                messages.error(request, "Unsupported file type.")
                return redirect('upload-file')
            
            file_summary = summarize(file_instance.file_text)
            file_tags = tag(file_instance.file_text)
            file_instance.file_summary = file_summary
            file_instance.file_tags = file_tags
            file_instance.host = request.user
            file_instance.save()
            form.save_m2m()  # Save the tags
            return redirect('view-files')
        else:
            messages.error(request, "File could not be uploaded")
    else:
        form = FileUploadForm()
    return render(request, 'pages/upload.html', {'form': form, 'user_files': user_files.count()})

@login_required(login_url='login')
def delete_file(request, pk):
    file = File.objects.get(id=pk)
    if file.host != request.user:
        return render(request, 'pages/restricted.html')
    file.delete()
    return redirect('view-files-list')

@login_required(login_url='login')
def view_files_grid(request):
    try:
        user_files = File.objects.filter(host=request.user)
        if not user_files.exists():
            user_files = []
            image_url = ''
        else:
            for file in user_files:
                image_url = static(f'images/{file.file_type}.png')
                file.file_size = round(file.file_size / (1024 * 1024), 2)
        return render(request, 'pages/view-files-grid.html', {'files': user_files, 'image_url': image_url})
    except Exception as e:
        return render(request, 'pages/view-files-grid.html', {'files': [], 'image_url': '', 'error': str(e)})

@login_required(login_url='login')
def view_files_list(request):
    try:
        user_files = File.objects.filter(host=request.user)
        if not user_files.exists():
            user_files = []
            image_url = ''
        else:
            for file in user_files:
                image_url = static(f'images/{file.file_type}.png')
                file.file_size = round(file.file_size / (1024 * 1024), 2)
        return render(request, 'pages/view-files-list.html', {'files': user_files, 'image_url': image_url})
    except Exception as e:
        return render(request, 'pages/view-files-list.html', {'files': [], 'image_url': '', 'error': str(e)})

@login_required(login_url='login')
def file_details(request, pk):
    file = File.objects.get(id=pk)
    size = round(file.file_size / (1024 * 1024), 2)
    dialogues = Dialogue.objects.filter(file=pk)
    image_url = static(f'images/{file.file_type}.png')

    # Remove any ** from the file_summary
    if file.file_summary:
        file.file_summary = re.sub(r'\*\*', '', file.file_summary)
        file.file_summary = re.sub(r'\*', '', file.file_summary)
    for dialogue in dialogues:
        dialogue.answer = re.sub(r'\*\*', '', dialogue.answer)
        dialogue.answer = re.sub(r'\*', '', dialogue.answer)
    
    if request.method == 'POST':
        if dialogues.count() > 10 and request.user.user_plan == 'basic':
            return render(request, 'pages/renew-plan.html')
        user_query = request.POST.get('query', '')

        if user_query:
            # Prepare the data for the API request
            data = {
                "model": "gemini-pro",
                "contents": f"{user_query} {file.file_text}"
            }
            headers = {
                "Content-Type": "application/json"
            }

            try:
                # Make the API request
                response = requests.post("https://datacubeai.pythonanywhere.com/api/generate", 
                                         headers=headers, 
                                         data=json.dumps(data))

                if response.status_code == 200:
                    ai_response = response.json().get('response', '')

                    # Store the dialogue in the database
                    dialogue = Dialogue(query=user_query, answer=ai_response)
                    dialogue.file = file
                    dialogue.host = request.user
                    dialogue.save()

                    return redirect('file-details', pk=pk)
                else:
                    messages.error(request, "Failed to get a response from the AI API.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    
    context = {'file': file, 'size': size, 'dialogues': dialogues, 'image_url': image_url, 'ai_queries': dialogues.count()}
    return render(request, 'pages/file-details.html', context)

@login_required(login_url='login')
def user_profile(request):
    user = Techie.objects.get(id=request.user.id)
    context = {'user': user}
    return render(request, 'pages/profile.html', context)

@login_required(login_url='login')
def search_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    docs = File.objects.filter(host=request.user)
    docs = File.objects.filter(
        Q(fname__icontains=q) | 
        Q(file_text__icontains=q) | 
        Q(file_type__icontains=q) | 
        Q(file_tags__icontains=q) | 
        Q(file_summary__icontains=q)
    )
    for doc in docs:
        doc.file_summary = re.sub(r'\*\*', '', doc.file_summary)
        docs.file_summary = re.sub(r'\*\*', '', doc.file_summary)

    chat = Dialogue.objects.filter(
        Q(query__icontains=q) | 
        Q(answer__icontains=q)
    )
    for query in chat:
        query.answer = re.sub(r'\*\*', '', query.answer)
        query.answer = re.sub(r'\*', '', query.answer)
    count = docs.count() + chat.count()
    context = {'docs': docs, 'count': count, 'query': q, 'chat': chat}
    
    return render(request, 'pages/search.html', context)

@login_required(login_url='login')
def under_construction(request):
    return render(request, 'pages/under-construction.html')
@login_required(login_url='login')
def pricing(request):
    return render(request, 'pages/pricing.html')



