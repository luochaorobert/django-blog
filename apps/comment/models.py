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

    def has_child(self):
        if self.comment_set.all().count() > 0:
            return True
        else:
            return False

    @classmethod
    def latest_comments(cls, nums=None):
        if nums:
            return cls.objects.filter(is_deleted=False).order_by('-created_time')[:nums]
        else:
            return cls.objects.filter(is_deleted=False).order_by('-created_time')

    @classmethod
    def get_comment_tree(cls, article, comment=None):
        """
        将指定Article实例的某个Comment实例的子评论生成树形结构，
        如果不指定Comment实例，则生成Article实例所有评论的树形结构
        返回结构示例：
        [
            {
                'current': obj,
                'subordinate': [],
            },
            {
                'current': obj,
                'subordinate': [
                    {
                        'current': obj,
                        'subordinate': [],
                    },
                    {
                        'current': obj,
                        'subordinate': [],
                    },
                ],
            },
            {
                'current': obj,
                'subordinate': [],
            }
        ]
        :param article: Article实例
        :param comment: Comment实例，可以不指定，默认为None
        :return: list
        """
        tree = []
        objects = cls.objects.filter(article=article, parent_comment=comment, is_deleted=False)
        for obj in objects:
            if obj.has_child:
                subordinate = cls.get_comment_tree(article, obj)
            else:
                subordinate = []
            tree.append({
                'current': obj,
                'subordinate': subordinate,
            })
        return tree
