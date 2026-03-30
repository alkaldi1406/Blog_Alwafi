from django.contrib import admin
from blog.models import Post, Comment
from .models import Post
from django import forms
from taggit.models import Tag

# Register your models here.

#
#
# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ['title','slug', 'author', 'published','status'] #لعرض القوائم داخل الـ post
#     list_filter = ['published','status','created']# لفلترة القوائم
#     search_fields = ['title', 'content']# هذه خاصية البحث بالعنوان او المحتوى
#     date_hierarchy = 'published'# خاصية البحث بالتاريخ
#     ordering = ['-published','status']# هذه خاصية الترتيب
#     prepopulated_fields = {'slug': ('title',)}# توليد الـ slug اوتوماتيكي بناء على الـ title
#     raw_id_fields = ('author',)# لتحويل القائمة المنسدلة الى حقل بحث بالمعرف للمستخدمين




@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created', 'active')
    # التعديل الجوهري: يجلب بيانات الكاتب والمقال في خبطة واحدة
    list_select_related = ['author', 'post']
    list_filter = ('active', 'created')
    search_fields = ('author__username', 'body')
    list_editable = ['active']
    list_per_page = 20  # يعرض ٢٠ تعليق فقط في الصفحة عشان ما يثقل المتصفح


class PostAdminForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(), # مربعات اختيار بدلاً من نص
        required=False
    )
    class Meta:
        model = Post
        fields = '__all__'




@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ['title', 'author', 'status', 'published']
    # تسريع عرض القائمة بجلب بيانات الكاتب فوراً
    list_select_related = ['author']
    # إضافة شريط بحث وسهولة في الوصول
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20

