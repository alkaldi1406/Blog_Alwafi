from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.forms import UserRegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .tokens import account_activation_token


# Create your views here.




def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # الحساب معطل حتى التفعيل
            user.save()

            # 2. التأكد من حفظ الإيميل والأسماء من الفورم للموديل
            user.email = form.cleaned_data.get('email')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()

            # 3. إرسال إيميل التفعيل (نفس الكود اللي سويناه فوق)
            current_site = get_current_site(request)
            mail_subject = 'تفعيل حسابك في مدونة الوافي'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            # 4. عرض صفحة "افتح إيميلك"
            return render(request, 'registration/check_email.html')
        else:
            # إذا فيه أخطاء (مثلاً الباسوورد ما تطابق) تظهر للمستخدم
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})






def activate(request, uidb64, token):
    try:
        # فك تشفير المعرف (ID)
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # التحقق من أن المستخدم موجود وأن "التوكن" صحيح ولم يُستخدم من قبل
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # حركة "دلع": تسجيل دخول المستخدم فوراً بعد التفعيل
        login(request, user, backend='accounts.backends.EmailOrUsernameBackend')

        messages.success(request, f'مرحباً {user.first_name}! تم تفعيل حسابك بنجاح.')
        return redirect('blog:index')  # وجهه للرئيسية فوراً
    else:
        # إذا كان الرابط قديم أو مستخدم أو فيه خطأ
        return render(request, 'registration/activation_invalid.html')




@login_required
def profile(request):
    # 1. السحر هنا: نسحب المستخدم مع بروفايله بضربة واحدة بدلاً من get_or_create
    user = User.objects.select_related('profile').get(id=request.user.id)
    user_profile = user.profile

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'تم تحديث حسابك بنجاح!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user_profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)
