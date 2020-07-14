from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.blog.models import Article
from .forms import CommentForm


class AddCommentView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def post(self, request, article_id, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        instance_id = 0
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.article = get_object_or_404(Article, id=article_id)
            instance.author = request.user
            instance.save()
            instance_id = instance.id

        return HttpResponseRedirect(
            reverse("article-detail", kwargs={'article_id': article_id}) +
            ("#commentBlock" + str(instance_id)) if instance_id else ""
        )
