from django.contrib import admin

from .models import Link, SideBar, BlogSettings


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'href', 'is_enable', 'weight', 'owner', 'created_time')
    fields = ('name', 'href', 'is_enable', 'weight')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(LinkAdmin, self).save_model(request, obj, form, change)


@admin.register(SideBar)
class SideBarAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'content', 'is_enable', 'order', 'owner', 'created_time')
    fields = ('title', 'type', 'content', 'is_enable', 'order')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(SideBarAdmin, self).save_model(request, obj, form, change)


@admin.register(BlogSettings)
class BlogSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_description', 'background_image', 'per_page_count',
                    'article_sub_length', 'sidebar_article_count', 'sidebar_comment_count',
                    'open_site_comment', 'theme', 'record_number', 'is_enable', 'created_time')
    fields = ('site_name', 'site_description', 'background_image', 'per_page_count',
              'article_sub_length', 'sidebar_article_count', 'sidebar_comment_count',
              'open_site_comment', 'theme', 'record_number', 'is_enable')
