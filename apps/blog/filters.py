import django_filters
from django.db.models import Q
from django import forms
from .models import Article, Category, Tag


class ArticleFilter(django_filters.FilterSet):
    key = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
                                    method='key_custom_filter', label="搜索关键词")
    category = django_filters.ModelChoiceFilter(widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        method='category_custom_filter', queryset=Category.objects.filter(is_deleted=False), label="文章分类")
    tag = django_filters.ModelChoiceFilter(widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        field_name='tag', queryset=Tag.objects.filter(is_deleted=False), label="文章标签")
    pub_time__gte = django_filters.NumberFilter(widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
        field_name='pub_time', lookup_expr='year__gte', label="发表年份(>=)")

    class Meta:
        model = Article
        fields = {}

    def key_custom_filter(self, queryset, name, value):
        return Article.objects.filter(is_published=True).filter(
            Q(title__icontains=value) | Q(desc__icontains=value) | Q(content__icontains=value)
        )

    def category_custom_filter(self, queryset, name, value):
        return Article.objects.filter(is_published=True).filter(
            Q(category_id__exact=value) | Q(category__parent_category_id__exact=value)
        )
