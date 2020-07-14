import os
import hashlib

from django.db import models
from django.template.loader import render_to_string
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Link(models.Model):
    """友情链接"""
    name = models.CharField(max_length=50, unique=True, verbose_name="链接名称")
    href = models.URLField(verbose_name="链接")  # 默认长度200
    is_enable = models.BooleanField(default=True, verbose_name="是否展示")
    weight = models.PositiveIntegerField(default=1, choices=zip(range(1, 6), range(1, 6)),
                                         verbose_name="权重", help_text="权重高展示顺序靠前")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="作者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "友链"
        verbose_name_plural = verbose_name
        ordering = ['-weight', ]

    def __str__(self):
        return self.name

    @classmethod
    def get_display(cls):
        return cls.objects.filter(is_enable=True).order_by('-weight')


class SideBar(models.Model):
    """侧边栏"""

    class DisplayType(models.IntegerChoices):
        HTML = 1, _('HTML')
        TAGS = 2, _('标签统计')
        LATEST_ARTICLES = 3, _('最新文章')
        HOTTEST_ARTICLES = 4, _('最热文章')
        LATEST_COMMENTS = 5, _('最近评论')
        LINK = 6, _('友情链接')

    title = models.CharField(max_length=50, verbose_name="标题")
    type = models.PositiveIntegerField(default=1, choices=DisplayType.choices, verbose_name="展示类型")
    content = models.TextField(blank=True, verbose_name="内容", help_text="如果设置的不是HTML类型，可为空")
    is_enable = models.BooleanField(default=True, verbose_name="是否展示")
    order = models.IntegerField(unique=True, verbose_name="排序")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="作者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "侧边栏"
        verbose_name_plural = verbose_name
        ordering = ['order']

    def __str__(self):
        return self.title

    def content_html(self):
        """渲染模板"""
        from apps.blog.models import Article, Tag  # 避免循环引用
        from apps.comment.models import Comment
        from utils.blog_setting import get_blog_setting

        result = ''
        if self.type == self.DisplayType.HTML:
            result = self.content
        elif self.type == self.DisplayType.TAGS:
            context = {
                'tags': Tag.objects.filter(is_deleted=False).order_by('created_time')
            }
            result = render_to_string('config/blocks/sidebar_tags.html', context)
        elif self.type == self.DisplayType.LATEST_ARTICLES:
            context = {
                'articles': Article.latest_articles(get_blog_setting()['sidebar_article_count'])
            }
            result = render_to_string('config/blocks/sidebar_latest_articles.html', context)
        elif self.type == self.DisplayType.HOTTEST_ARTICLES:
            context = {
                'articles': Article.hottest_articles(get_blog_setting()['sidebar_article_count'])
            }
            result = render_to_string('config/blocks/sidebar_hottest_articles.html', context)
        elif self.type == self.DisplayType.LATEST_COMMENTS:
            context = {
                'comments': Comment.latest_comments(get_blog_setting()['sidebar_comment_count'])
            }
            result = render_to_string('config/blocks/sidebar_comments.html', context)
        elif self.type == self.DisplayType.LINK:
            context = {
                'links': Link.get_display()
            }
            result = render_to_string('config/blocks/sidebar_links.html', context)
        return result


def background_image_path(instance, filename):
    content = instance.background_image.file.read()
    ext = filename.split('.')[-1]
    # 将上传的图片文件命名为md5值
    filename = '{}.{}'.format(hashlib.md5(content).hexdigest(), ext)
    return os.path.join("background_image", filename)


class BlogSettings(models.Model):
    """站点设置"""

    class ThemeChoice(models.IntegerChoices):
        default = 1, _('默认主题')
        other = 2, _('其他主题')

    site_name = models.CharField(max_length=200, verbose_name="网站名称")
    site_description = models.TextField(max_length=1000, default='', verbose_name="网站描述")
    background_image = models.ImageField(upload_to=background_image_path, blank=True, null=True,
                                         verbose_name="背景图片")
    per_page_count = models.IntegerField(default=10, verbose_name="文章列表每页数目")
    article_sub_length = models.IntegerField(default=200, verbose_name="文章摘要长度")
    sidebar_article_count = models.IntegerField(default=5, verbose_name="侧边栏文章数目")
    sidebar_comment_count = models.IntegerField(default=5, verbose_name="侧边栏评论数目")
    open_site_comment = models.BooleanField(default=True, verbose_name="是否打开网站评论功能")
    theme = models.PositiveIntegerField(default=1, choices=ThemeChoice.choices, verbose_name="模板主题")
    record_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="网站备案号")
    is_enable = models.BooleanField(default=False, verbose_name="是否启用")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '网站配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site_name

    def clean(self):
        if BlogSettings.objects.filter(is_enable=True).count() > 1:
            raise ValidationError(_('只能有一个启用的配置'))
