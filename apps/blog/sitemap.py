from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article


class ArticleSitemap(Sitemap):
    changefreq = "always"
    priority = 1.0
    protocol = 'https'

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.created_time

    def location(self, obj):
        return reverse('article-detail', args=[obj.pk])
