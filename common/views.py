from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy


from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth

from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy

from allauth.socialaccount.models import SocialAccount

from common.models import UserProfile
from common.forms import ProfileCreationForm


def index(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
        # сначала читаем таблицу профилей своих пользователей
        request_user_profile = UserProfile.objects.filter(
            user=request.user).first()
        if request_user_profile:
            context['auth_type'] = 1
            context['age'] = request_user_profile.age
        else:
            context['auth_type'] = 2
            context['github_url'] = SocialAccount.objects.get(
                provider='github', user=request.user).extra_data['html_url']
            context['public_repos'] = SocialAccount.objects.get(
                provider='github', user=request.user).extra_data['public_repos']
            context['created_at'] = SocialAccount.objects.get(
                provider='github', user=request.user).extra_data['created_at']

    return render(request, 'index.html', context)


class RegisterView(FormView):

    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        login(self.request, authenticate(
            username=username, password=raw_password))
        return super(RegisterView, self).form_valid(form)


class CreateUserProfile(FormView):

    form_class = ProfileCreationForm
    template_name = 'profile-create.html'
    success_url = reverse_lazy('common:index')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return HttpResponseRedirect(reverse_lazy('common:login'))
        return super(CreateUserProfile, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return super(CreateUserProfile, self).form_valid(form)
