"""django_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from django.conf import settings
from django.contrib.sitemaps import views as sitemap_views
from django.views.generic import TemplateView

from apps.blog.rss import LatestPostFeed
from apps.blog.sitemap import ArticleSitemap

from apps.blog.views import ArticleListView, ArticleDetailView, ArticleArchivesView
from apps.users.views import ProfileView
from apps.comment.views import AddCommentView

handler404 = 'apps.blog.views.page_not_found_view'
handler500 = 'apps.blog.views.server_error_view'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ArticleListView.as_view(), name='article-list'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/<int:user_id>/', ProfileView.as_view(), name="profile"),
    path('article/<int:article_id>/', ArticleDetailView.as_view(), name='article-detail'),
    path('add_comment/<int:article_id>/', AddCommentView.as_view(), name='add-comment'),
    path('archives/', ArticleArchivesView.as_view(), name='article-archives'),
    path('rss/', LatestPostFeed(), name='rss'),
    path('sitemap.xml', sitemap_views.sitemap, {'sitemaps': {'articles': ArticleSitemap}}, name='sitemap'),
    path('mdeditor/', include('mdeditor.urls')),

    # 配置上传文件的访问url
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
]
