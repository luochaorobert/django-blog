from django.db import models
from django.conf import settings

from apps.blog.models import Article


class Comment(models.Model):
    """用户评论"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="文章")
    content = models.TextField(max_length=2000, verbose_name="评论内容")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="作者")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="上级评论")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    mod_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    @classmethod
    def latest_comments(cls):
        return cls.objects.filter(is_deleted=False).order_by('-created_time')

    @classmethod
    def get_by_target(cls, target):
        return cls.objects.filter(target=target, status=cls.STATUS_NORMAL)
