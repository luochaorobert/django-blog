import os
import hashlib

from django.db import models
from django.contrib.auth.models import AbstractUser


def user_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(instance.name, ext)
    return os.path.join("head_image", str(instance.id), filename)


class UserProfile(AbstractUser):
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='昵称')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号码")
    image = models.ImageField(upload_to=user_image_path, default="head_image/default.jpg",
                              verbose_name="用户头像")
    homepage = models.URLField(null=True, blank=True, verbose_name="个人主页")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        content = self.image.file.read()
        # 将上传的图片文件命名为md5值
        self.name = hashlib.md5(content).hexdigest()
        super().save(*args, **kwargs)
