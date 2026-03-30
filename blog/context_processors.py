# في ملف context_processors.py
def notifications_count(request):
    if request.user.is_authenticated:
        # استخدام count() مباشرة سريع جداً في قاعدة البيانات
        count = request.user.notifications.filter(is_read=False).count()
        # جلب آخر 5 إشعارات مع بيانات المرسل لسرعة العرض في القائمة
        latest_notifications = request.user.notifications.select_related('sender__profile', 'post').all()[:5]
    else:
        count = 0
        latest_notifications = []
    return {
        'unread_notifications_count': count,
        'latest_notifications': latest_notifications
    }
