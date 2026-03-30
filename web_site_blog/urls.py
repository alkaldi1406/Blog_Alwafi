"""
URL configuration for web_site_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView

from blog.feeds import LatestPostsFeed
from blog.sitemaps import PostSitemap


# قاموس يحتوي على جميع أصناف الخرائط (يمكنك إضافة خرائط للأقسام أو الصفحات الثابتة هنا)
sitemaps = {
    'posts': PostSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('accounts/',include('accounts.urls')),

    # تعريف المسار الذي سيظهر عليه ملف الـ XML
    # نمرر قاموس 'sitemaps' للـ View ليقوم بتوليد الروابط تلقائياً
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

      # مسار ملف robots.txt
    path(
          "robots.txt",  # تأكد أنها .txt وليست .xml
          TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),

                  # RSS feed مذياع المقالات
    path('feed/', LatestPostsFeed(), name='post_feed'),


] + debug_toolbar_urls()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)