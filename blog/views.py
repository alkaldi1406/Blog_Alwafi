from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.text import slugify
from taggit.models import Tag
from blog.forms import EmailPostForm, CommentForm, PostCreateForm
from blog.models import Post, Comment, Notification
from django.contrib import messages



# Create your views here.




# @login_required
def index(request, tag_slug=None):

    post_list = Post.objects.filter(status=Post.Status.PUBLISHED) \
        .select_related('author__profile') \
        .prefetch_related('tags') \
        .annotate(total_likes=Count('likes'))  #  أضفنا annotate لحساب اللايكات في استعلام واحد فقط

    # 2. جلب جميع التاغات لعرضها في "تصفح حسب المواضيع"
    all_tags = Tag.objects.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # 3. نظام البحث
    query = request.GET.get('q')
    if query:
        post_list = post_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).distinct()

    # 4. الترتيب (يفضل دائماً الترتيب قبل الترقيم)
    post_list = post_list.order_by('-published')

    # 5. الترقيم (Pagination)
    paginator = Paginator(post_list, 12)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {
        'posts': posts,
        'tag': tag,
        'all_tags': all_tags,
    })


@login_required
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url()) # هنا نصنع الرابط الكامل للمقالة (زي اللي بننسخه من المتصفح) عشان نقدر نرسله في الإيميل

            # إعداد محتوى الإيميل
            subject = f"اقتراح قراءة: {post.title} من صديقك {cd['name']}"
            from_email = f"موقع الوافي <{settings.EMAIL_HOST_USER}>"
            to = [cd['to']]

            # تحميل قالب الـ HTML وتمرير البيانات له
            html_content = render_to_string('blog/email_template.html', {
                'post': post,
                'post_url': post_url,
                'name': cd['name'],
                'comment': cd['comment']
            })
            text_content = strip_tags(html_content)  # نسخة نصية احتياطية

            email = EmailMultiAlternatives(subject, text_content, from_email, to)
            email.attach_alternative(html_content, "text/html")
            email.send()

            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/share.html', {'post': post, 'form': form, 'sent': sent})





# @login_required

def post_detail(request, year, month, day, slug):
    # 1. سحب المقال مع الكاتب، البروفايل، التاغات، واللايكات بضربة واحدة
    # أضفنا 'likes' هنا لمنع الاستعلامات المكررة التي ظهرت باللون الموف في صورتك
    post = get_object_or_404(
        Post.objects.select_related('author__profile')
                    .prefetch_related('tags', 'likes'),
        slug=slug,
        published__year=year,
        published__month=month,
        published__day=day
    )

    # 2. تحسين المقالات المشابهة
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids, status=Post.Status.PUBLISHED)\
                               .exclude(id=post.id)\
                               .select_related('author__profile')\
                               .prefetch_related('tags')\
                               .annotate(same_tags=Count('tags'))\
                               .order_by('-same_tags', '-published')[:4]

    # 3. عداد المشاهدات الذكي (Session Based)
    session_key = f'viewed_post_{post.id}'
    if not request.session.get(session_key, False):
        post.views_count += 1
        post.save(update_fields=['views_count'])
        request.session[session_key] = True

    # 4. تحسين التعليقات والردود وأصحابها بروفايلاتهم
    comments = post.comments.filter(active=True, parent__isnull=True)\
                            .select_related('author__profile')\
                            .prefetch_related('replies__author__profile')

    # 5. معالجة إرسال التعليقات والردود
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user

            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                new_comment.parent = parent_obj
                msg = 'تم إضافة ردك بنجاح!'
            else:
                msg = 'تم إضافة تعليقك بنجاح!'

            new_comment.save()
            messages.success(request, msg)
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
    })




@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    # إضافة رابط افتراضي "/" في حال كان الـ Referer غير موجود
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))




@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user

            # معالجة الـ Slug مع دعم العربي وضمان عدم التكرار
            base_slug = slugify(new_post.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            # إذا الـ slug موجود، ضيف عليه رقم (عشان ما يضرب الـ Unique)
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            new_post.slug = slug
            new_post.status = Post.Status.DRAFT
            new_post.save()
            form.save_m2m()
            messages.success(request, 'تم إرسال مقالك بنجاح وهو قيد المراجعة!')
            return redirect('blog:index')
    else:
        form = PostCreateForm()
    return render(request, 'blog/post_form.html', {'form': form})





@login_required
def user_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied

    user_posts = Post.objects.filter(author=request.user) \
        .annotate(
            total_likes_count=Count('likes', distinct=True),
            total_comments_count=Count('comments', distinct=True) # السحر هنا
        ) \
        .order_by('-created')

    return render(request, 'blog/dashboard.html', {'user_posts': user_posts})





@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)  # حماية: يعدل مقاله بس!
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES, instance=post)  # السحر هنا في instance
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المقال بنجاح!')
            return redirect('blog:user_dashboard')
    else:
        form = PostCreateForm(instance=post)  # يعبي الفورم ببيانات المقال القديمة

    return render(request, 'blog/post_form.html', {'form': form, 'is_edit': True})





@login_required
def post_delete(request, post_id):
    # جلب المقال والتأكد أن المستخدم هو صاحبه
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'تم حذف المقال وصورته نهائياً بنجاح!')  # Cleanup ستعمل هنا تلقائياً
        return redirect('blog:user_dashboard')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})





def user_posts(request, username):
    # جلب المستخدم أو إظهار 404 إذا لم يوجد
    author = get_object_or_404(User, username=username)
    # جلب مقالات هذا الكاتب فقط (المنشورة)
    posts = Post.objects.filter(author=author, status=Post.Status.PUBLISHED).order_by('-published').annotate(total_likes=Count('likes'))

    return render(request, 'blog/user_posts.html', {
        'author': author,
        'posts': posts
    })




@login_required
def mark_notification_as_read(request, notification_id):
    # جلب الإشعار والتأكد أنه يخص المستخدم الحالي (حماية)
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()

    # توجيه المستخدم لصفحة المقال فوراً
    return redirect(notification.post.get_absolute_url())



@login_required
def mark_all_as_read(request):
    # تحديث كل الإشعارات غير المقروءة لهذا المستخدم فقط
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة ✅')
    return redirect(request.META.get('HTTP_REFERER', 'blog:index')) # يرجعه لنفس الصفحة





@login_required
def post_like_ajax(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        post = get_object_or_404(Post, id=post_id)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            status = "unliked"
        else:
            post.likes.add(request.user)
            status = "liked"

        # نرجع الـ total_likes الجديد (تأكد من وجود related_name='likes' في الموديل)
        return JsonResponse({
            'status': status,
            'total_likes': post.likes.count()
        })
