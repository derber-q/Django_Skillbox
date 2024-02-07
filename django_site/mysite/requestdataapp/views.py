from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UserBioForms, UploadFileForm

def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'resul': result
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)

def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        'form': UserBioForms(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = request.FILES.get("myfile")
            if request.FILES.get("myfile").size < 104857600:
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                print('Saved file', filename)
            else:
                context = {
                    'error': 'Invalid file size (The file size must not exceed: 100mb)'
                }
                return render(request, 'requestdataapp/error.html', context=context)
    form = UploadFileForm()
    context = {
        'form': form,
    }
    return render(request, 'requestdataapp/file-upload.html',context=context)

