import re

from django import forms
from django.core.cache import cache
from django.forms import inlineformset_factory, BaseInlineFormSet

from apps.users.models import UserProfile


class ProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ["nickname", "mobile", "homepage", "image"]

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]
        if not mobile:
            return None

        # 验证手机号码是否合法
        regex_mobile = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(regex_mobile)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError("手机号码格式有误", code="mobile_invalid")
