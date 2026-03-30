from django import template
from ..models import Post
from django.db.models import Count

register = template.Library()


#هذا هو الـ simple_ta
@register.simple_tag
def total_posts():
    # 2. نطلب من قاعدة البيانات عدد المقالات المنشورة فقط
    return Post.objects.filter(status=Post.Status.PUBLISHED).count()




# هذا هو الـ Inclusion Tag
@register.inclusion_tag('blog/latest_posts.html')
def show_latest_posts(count=5):
    # بنجيب أحدث المقالات المنشورة حسب العدد المطلوب
    latest_posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-published')[:count]

    # بنرسلهم لملف HTML صغير (قالب فرعي)
    return {'latest_posts': latest_posts}





@register.inclusion_tag('blog/most_commented.html')
def get_most_commented_posts(count=5):
    # 1. نجلب المقالات المنشورة
    # 2. annotate: نصنع حقل وهمي اسمه total_comments ونضع فيه عدد التعليقات
    # 3. order_by: نرتب تنازلياً حسب هذا الحقل الجديد
    most_commented_posts = Post.objects.filter(status=Post.Status.PUBLISHED) \
        .annotate(total_comments=Count('comments')) \
        .order_by('-total_comments')[:count]

    return {'most_commented_posts': most_commented_posts}
