from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'content', 'author', 'parent_comment', 'is_deleted', 'created_time', 'mod_time')
