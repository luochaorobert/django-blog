from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import UserProfile
from .forms import ProfileForm


class ProfileView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(UserProfile, id=user_id)
        profile_form = ProfileForm(instance=user)
        context = {
            "user": user,
            "form": profile_form,
            "is_self": request.user == user,
        }
        return render(request, "account/profile.html", context=context)

    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(UserProfile, id=user_id)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user)
        if profile_form.is_valid():
            profile_form.save()
        context = {
            "user": user,
            "form": profile_form,
            "is_self": request.user == user,
        }

        return render(request, "account/profile.html", context=context)
