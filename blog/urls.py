from django.urls import path

from blog.feeds import LatestPostsFeed
from blog.views import index, post_share, post_detail, post_like, post_create, user_dashboard, post_edit, post_delete, \
    user_posts, mark_notification_as_read, mark_all_as_read, post_like_ajax

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('tag/<str:tag_slug>/', index, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<str:slug>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/', post_share, name='post_share'),
    path('like/<int:post_id>/', post_like, name='post_like'),
    path('create/', post_create, name='post_create'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('edit/<int:post_id>/', post_edit, name='post_edit'),
    path('delete/<int:post_id>/', post_delete, name='post_delete'),
    path('user/<str:username>/', user_posts, name='user_posts'),
    # تأكد من وجود app_name = 'blog' في أعلى الملف
    path('notification/read/<int:notification_id>/', mark_notification_as_read, name='mark_as_read'),
    path('notifications/read-all/', mark_all_as_read, name='mark_all_read'),
    path('like-ajax/', post_like_ajax, name='post_like_ajax'),
    # إضافة رابط الـ RSS
    path('feed/', LatestPostsFeed(), name='post_feed'),


]