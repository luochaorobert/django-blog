from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.urls import reverse
from django.utils.html import format_html

from .models import Article, Category, Tag


class ArticleInline(admin.TabularInline):  # StackedInline  样式不同
    fields = ('title', 'desc')
    extra = 1  # 控制额外多几个
    model = Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ArticleInline, ]
    list_display = ('name', 'parent_category', 'sort', 'is_deleted', 'is_nav', 'owner', 'created_time')
    fields = ('name', 'parent_category', 'is_deleted', 'is_nav', 'sort')
    list_editable = ['sort']

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

    def article_count(self, obj):
        return obj.article_set.count()

    article_count.short_description = '文章数量'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_deleted', 'owner', 'created_time')
    fields = ('name', 'is_deleted')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'author', 'on_top', 'comment_allowed', 'is_published',
        'pub_time', 'created_time', 'mod_time', 'users_like_count', 'pv', 'uv', 'operator'
    ]
    list_display_links = []
    list_editable = ['comment_allowed', 'is_published']
    search_fields = ['title', 'category__name']
    exclude = ['owner']

    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True

    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                ('is_published', 'on_top', 'comment_allowed'),
            ),
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('wide',),
            'fields': ('tag', ),
        })
    )
    # filter_horizontal = ('tag', )
    filter_vertical = ('tag', )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        return super(ArticleAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(owner=request.user)
        if db_field.name == "tag":
            kwargs["queryset"] = Tag.objects.filter(owner=request.user)
        return super(ArticleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('admin:blog_article_change', args=(obj.id,))
        )
    operator.short_description = '操作'
