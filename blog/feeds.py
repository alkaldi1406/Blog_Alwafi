from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


# الـ RSS Feed هو "المذياع" الخاص بمدونتك.
# وظيفته: يبث أخبارك الجديدة فوراً للمتابعين المشتركين.
# الفائدة: يحول "الزائر العابر" إلى "متابع دائم"، ويسهل عملية مشاركة مقالاتك
# تلقائياً في منصات التواصل الاجتماعي.


class LatestPostsFeed(Feed):
    title = "مدونة الوافي - آخر المقالات" # اسم الخلاصة
    link = "/rss/" # الرابط
    description = "ابقَ على اطلاع بأحدث المقالات التقنية والعلمية في مدونة الوافي."

    def items(self):
        # نجلب آخر 5 مقالات منشورة فقط
        return Post.objects.filter(status='PB').order_by('-published')[:5]

    def item_title(self, item):
        return item.title # عنوان المقال في الخلاصة

    def item_description(self, item):
        return item.content[:150] # نبذة قصيرة من المقال
