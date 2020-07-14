from django.core.cache import cache
from apps.config.models import BlogSettings


def get_blog_setting():
    value = cache.get('blog_setting')
    if value:
        return value
    else:
        blog_settings = BlogSettings.objects.filter(is_enable=True)
        if blog_settings:
            value = {
                'site_name': blog_settings[0].site_name,
                'site_description': blog_settings[0].site_description,
                'background_image': blog_settings[0].background_image.url,
                'per_page_count': blog_settings[0].per_page_count,
                'article_sub_length': blog_settings[0].article_sub_length,
                'sidebar_article_count': blog_settings[0].sidebar_article_count,
                'sidebar_comment_count': blog_settings[0].sidebar_comment_count,
                'open_site_comment': blog_settings[0].open_site_comment,
                'theme': blog_settings[0].theme,
                'record_number': blog_settings[0].record_number,
            }
        else:
            value = {
                'site_name': '一个博客',
                'site_description': '这是一个用Django开发的博客',
                'background_image': '',
                'per_page_count': 10,
                'article_sub_length': 200,
                'sidebar_article_count': 5,
                'sidebar_comment_count': 5,
                'open_site_comment': True,
                'theme': 1,
                'record_number': '还没有备案',
            }
        cache.set('blog_setting', value, 30 * 60)
        return value
