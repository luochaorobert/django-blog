import pprint
import logging
from datetime import date

from django.core.cache import cache
from django.db.models import Q, F
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404

from apps.config.models import SideBar, BlogSettings
from apps.comment.models import Comment
from .models import Article, Category, Tag
from .filters import ArticleFilter
from apps.comment.forms import CommentForm

from utils.blog_setting import get_blog_setting


class CommonViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sidebars': self.get_sidebars(),
            'filter_form': ArticleFilter(self.request.GET, queryset=Article.objects.filter(is_published=True)).form,
            'category_tree': Category.get_category_tree(),
            'blog_setting': get_blog_setting(),
        })
        return context

    def get_sidebars(self):
        return SideBar.objects.filter(is_enable=True)


class ArticleListView(CommonViewMixin, ListView):
    paginate_by = get_blog_setting()['per_page_count']
    context_object_name = 'article_list'
    template_name = 'blog/list.html'

    def get_queryset(self):
        filter_queryset = ArticleFilter(self.request.GET, queryset=Article.latest_articles()).qs
        return filter_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form = ArticleFilter(self.request.GET, queryset=Article.latest_articles()).form
        filter_items = {}

        if filter_form.is_valid():
            for k, v in filter_form.cleaned_data.items():
                if v:
                    filter_items[filter_form.fields[k].label] = v

        context.update({
            'filter_items': filter_items,
        })
        return context


class ArticleDetailView(CommonViewMixin, DetailView):
    queryset = Article.objects.filter(is_published=True)
    template_name = 'blog/detail.html'
    context_object_name = 'article'
    pk_url_kwarg = 'article_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'comment_tree': Comment.get_comment_tree(self.object),
            'comment_form': CommentForm(),
        })
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.handle_visited()
        return response

    def handle_visited(self):
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        if not cache.get(pv_key):
            increase_pv = True
            cache.set(pv_key, 1, 1*60)  # 1分钟有效

        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)
        if not cache.get(uv_key):
            increase_uv = True
            cache.set(uv_key, 1, 24*60*60)  # 24小时有效

        if increase_pv and increase_uv:
            Article.objects.filter(pk=self.object.id).update(pv=F('pv') + 1, uv=F('uv') + 1)
        elif increase_pv:
            Article.objects.filter(pk=self.object.id).update(pv=F('pv') + 1)
        elif increase_uv:
            Article.objects.filter(pk=self.object.id).update(uv=F('uv') + 1)


class ArticleArchivesView(CommonViewMixin, ListView):
    queryset = Article.objects.filter(is_published=True).order_by('-pub_time')
    context_object_name = 'article_list'
    template_name = 'blog/archives.html'


def page_not_found_view(request, exception):
    return render(request, '404.html', context={}, status=404)


def server_error_view(request):
    return render(request, '50x.html', context={}, status=500)
