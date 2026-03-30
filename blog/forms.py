from django import forms
from taggit.models import Tag

from blog.models import Comment, Post


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسمك'}))
    to = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'بريد صديقك'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب تعليقك هنا...'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب تعليقك هنا...'}),
        }
        labels = {'body': ''}



class PostCreateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields =['title', 'content','image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'عنوان المقال...'}),
            'content': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 10, 'placeholder': 'اكتب محتوى المقال هنا...'}),
            'image': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
        }