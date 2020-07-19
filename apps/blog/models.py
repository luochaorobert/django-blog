import datetime

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.template.defaultfilters import truncatechars_html

import mistune
from mdeditor.fields import MDTextField


class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=50, verbose_name="分类名称")
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="父级分类")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    is_nav = models.BooleanField(default=True, verbose_name="是否为主页导航")
    sort = models.PositiveIntegerField(verbose_name="排序编号")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="创建者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        unique_together = (("name", "parent_category"),)
        ordering = ['sort']

    def __str__(self):
        return self.name

    def clean(self):
        # 已删除的分类必然不放在主页导航
        if self.is_deleted and self.is_nav:
            self.is_nav = False

    def has_child(self):
        if self.category_set.all().count() > 0:
            return True
        else:
            return False

    @classmethod
    def get_category_tree(cls, obj=None):
        """
        将obj所有的子分类生成树形结构，如果不指定则生成Category里所有分类的树形结构
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
        :param obj: Category实例，可以不指定，默认为None
        :return: list
        """
        tree = []
        objects = cls.objects.filter(parent_category=obj, is_nav=True)
        for obj in objects:
            if obj.has_child:
                subordinate = cls.get_category_tree(obj)
            else:
                subordinate = []
            tree.append({
                'current': obj,
                'subordinate': subordinate,
            })
        return tree


class Tag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名称")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="创建者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @cached_property
    def article_count(self):
        return Article.objects.filter(tag__name=self.name, is_published=True).distinct().count()

    article_count.short_description = "文章数量"


class Article(models.Model):
    """文章"""
    title = models.CharField(max_length=255, verbose_name="标题")
    desc = models.CharField(max_length=1024, blank=True, null=True, verbose_name="摘要")
    content = MDTextField(verbose_name="正文")
    content_html = models.TextField(verbose_name="正文html代码", blank=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name="分类")
    tag = models.ManyToManyField(Tag, verbose_name="标签", blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="作者")
    on_top = models.BooleanField(default=False, verbose_name="是否置顶")
    comment_allowed = models.BooleanField(default=True, verbose_name="是否允许评论")
    is_published = models.BooleanField(default=False, verbose_name="是否发布")
    pub_time = models.DateTimeField(null=True, verbose_name="发布时间")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    mod_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='articles_liked',
                                        blank=True, verbose_name="点赞用户")
    pv = models.PositiveIntegerField(default=0)
    uv = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ['-on_top', '-pub_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.content_html = mistune.markdown(self.content)
        super().save(*args, **kwargs)

    def clean(self):
        # 未发布的文章不应该有发布时间
        if not self.is_published and self.pub_time is not None:
            self.pub_time = None
        if self.is_published and self.pub_time is None:
            self.pub_time = datetime.datetime.now()
        # 置顶的文章必须是已发布的
        if self.on_top and not self.is_published:
            self.on_top = False

    def published(self):
        self.is_published = True
        self.pub_time = datetime.datetime.now()
        self.save(update_fields=['is_published', 'pub_time'])

    def next_article(self):
        # 下一篇文章
        return Article.objects.filter(
            pub_time__gt=self.pub_time, is_published=True).order_by('pub_time').first()

    def prev_article(self):
        # 前一篇文章
        return Article.objects.filter(
            pub_time__lt=self.pub_time, is_published=True).order_by('pub_time').last()

    @classmethod
    def latest_articles(cls, nums=None):
        if nums:
            return cls.objects.filter(is_published=True)[:nums]
        else:
            return cls.objects.filter(is_published=True)

    @classmethod
    def hottest_articles(cls, nums=None):
        if nums:
            return cls.objects.filter(is_published=True).order_by('-pv')[:nums]
        else:
            return cls.objects.filter(is_published=True).order_by('-pv')

    @cached_property
    def comment_num(self):
        return self.comment_set.filter(is_deleted=False).count()

    comment_num.short_description = "评论数量"

    @cached_property
    def tags(self):
        return ','.join(self.tag.values_list('name', flat=True))

    @cached_property
    def users_like_count(self):
        return self.users_like.all().count()

    users_like_count.short_description = "点赞数量"
