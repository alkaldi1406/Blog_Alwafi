from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF','draft'
        PUBLISHED = 'PB','published'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, allow_unicode=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    tags = TaggableManager()
    image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    likes = models.ManyToManyField(User, related_name='blog_posts_liked', blank=True)
    views_count = models.PositiveIntegerField(default=0)  # عداد المشاهدات




    class Meta:
        # 1. هذا "يأمر" قاعدة البيانات بالترتيب (عشان اليوزر يشوفها صح)
        ordering = ['-published']

        # 2. هذا "يجهز" الترتيب مسبقاً (عشان الموقع يكون سريع جدا)
        indexes = [
            models.Index(fields=['-published']), # فهرس للترتيب الزمني
            models.Index(fields=['status']),  # فهرس لسرعة جلب حالة "المنشورات" فقط
        ]



    def __str__(self):
        return self.title



    def get_absolute_url(self):# تُرجع الرابط الفريد الخاص بكل منشور لسهولة الوصول إليه في القوالب والتحويل التلقائي
        return reverse('blog:post_detail', args=[self.published.year,
                                                 "{:02d}".format(self.published.month),
                                                 self.published.day,
                                                 self.slug,
                                                 ])




class Comment(models.Model):

    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='replies')




    class Meta:
        ordering = ['created']  # ترتيب التعليقات من الأقدم للأحدث (مثل المحادثة)
        indexes = [
            models.Index(fields=['created']),  # فهرس عشان سرعة عرض التعليقات
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'





class Notification(models.Model):
    # أنواع الإشعارات (تعليق جديد، لايك جديد، إلخ)
    NOTIFICATION_TYPES = (
        ('comment', 'تعليق جديد'),
        ('like', 'إعجاب جديد'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications') # المستلم (صاحب المقال)
    sender = models.ForeignKey(User, on_delete=models.CASCADE) # المرسل (اللي علق)
    post = models.ForeignKey('Post', on_delete=models.CASCADE) # المقال المعني
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.CharField(max_length=255) # نص الإشعار
    is_read = models.BooleanField(default=False) # هل قرأه المستخدم؟
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']





    @receiver(post_save, sender=Comment)  # راقب جدول التعليقات
    def create_comment_notification(sender, instance, created, **kwargs):
        if created:  # إذا كان تعليق جديد (مو تعديل)
            # إذا كان المعلق مو هو نفسه كاتب المقال (عشان ما يجيه إشعار على تعليقه هو)
            if instance.author != instance.post.author:
                Notification.objects.create(
                    recipient=instance.post.author,
                    sender=instance.author,
                    post=instance.post,
                    notification_type='comment',
                    text=f'قام {instance.author.username} بالتعليق على مقالك: {instance.post.title}'
                )



