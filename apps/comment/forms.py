from django import forms

from apps.comment.models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["parent_comment", "content"]
        widgets = {
            'parent_comment': forms.HiddenInput(),
            'content': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'form-control'}),
        }

