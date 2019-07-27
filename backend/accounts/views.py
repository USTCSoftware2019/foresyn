from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserSignUpForm


class UserSignUp(CreateView):
    template_name = 'registration/signup.html'
    form_class = UserSignUpForm
    success_url = reverse_lazy('login')  # this router is loaded after accounts app, so use reverse_lazy
