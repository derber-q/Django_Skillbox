from random import random

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, CreateView, UpdateView, ListView

from .models import Profile
from .forms import ProfileForm
from django.utils.translation import gettext_lazy as _

class HelloView(View):
    def get(self, request:HttpRequest)->HttpResponse:
        welcome_message = _("Hello word!")
        return HttpResponse(f"<h1>{welcome_message}</h1>")

class AboutMeView(TemplateView):
    template_name ='myauth/about-me.html'

# def login_view(request: HttpRequest):
#     if request.method == 'GET':
#         if request.user.is_authenticated:
#             return redirect('/admin/')
#         return render(request, 'myauth/login.html')
#
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return redirect('/admin/')
#     return render(request, 'myauth/login.html', {'error': 'Invalid credentials'})

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')
    def form_valid(self, form):
        resource = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)
        return resource

class ProfileUpdateView(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = 'myauth:change_profile'
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy('myauth:profile-list')



    def test_func(self):
        return self.request.user.is_staff or self.request.user == self.get_object().user


class ProfileListView(ListView):
    template_name ='myauth/profile-list.html'
    queryset = Profile.objects.all()
    context_object_name = 'profiles'


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')

# def logout_view(request: HttpRequest) -> HttpResponse:
#     logout(request)
#     return redirect(reverse('myauth:login'))

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response

@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default value')
    return HttpResponse(f'Cookie value: {value!r} + {random()}')

@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')

@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default')
    return HttpResponse(f'Session value: f{value!r}')



class FoobBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})

class UserUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_user'
    model = Profile
    fields = 'user', 'bio', 'avatar'
    template_name_suffix = '_update_form'
    #form_class = ProductForm

    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().user
