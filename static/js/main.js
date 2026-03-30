document.addEventListener('DOMContentLoaded', function () {
    /* --- 1. إدارة التنبيهات (Toasts) --- */
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        var toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 4000 });
        toast.show();
    });
});

/* --- 2. نظام الردود (Comments) --- */
function setParent(commentId, authorName) {
    const parentInput = document.getElementById('parent_id');
    const formTitle = document.getElementById('form-title');
    const cancelBtn = document.getElementById('cancel-reply');
    if (parentInput && formTitle) {
        parentInput.value = commentId;
        formTitle.innerText = "الرد على: " + authorName;
        cancelBtn.classList.remove('d-none');
        document.getElementById('comment-add-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function cancelReply() {
    document.getElementById('parent_id').value = "";
    document.getElementById('form-title').innerText = "أضف تعليقاً جديداً";
    document.getElementById('cancel-reply').classList.add('d-none');
}

/* --- 3. محرك الإشعارات (الجرس) الصافي --- */
function toggleNotifications() {
    const menu = document.getElementById('noti-dropdown');
    if (menu) {
        const isHidden = menu.style.display === 'none' || menu.style.display === '';
        menu.style.display = isHidden ? 'block' : 'none';
    }
}

// إغلاق القائمة عند الضغط خارجها
window.addEventListener('click', function(e) {
    const menu = document.getElementById('noti-dropdown');
    const link = document.getElementById('bell-link');
    if (menu && !menu.contains(e.target) && link && !link.contains(e.target)) {
        menu.style.display = 'none';
    }
});
