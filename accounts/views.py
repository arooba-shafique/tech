from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .models import AdminManager
from .forms import AdminManagerForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.db.models import Q
User = get_user_model()


# ── Helper: safely read role without crashing on AnonymousUser ──────────────
def get_role(user):
    if user.is_authenticated and hasattr(user, 'role'):
        return user.role
    return None


# ── Login ────────────────────────────────────────────────────────────────────
# ❌ NO @login_required here — this IS the login page
def admin_login(request):
    # 1. Handle users who are already logged in
    if request.user.is_authenticated:
        role = get_role(request.user)
        
        # If they ARE a principal, let them through
        if role == "principal":
            return redirect("admin_console")
        
        # If they are not a principal, kick them out
        else:
            logout(request)
            # After logout, the code continues down to show the login form

    # 2. Handle Messages (Rest of your code is fine)
    msg = request.GET.get("msg")
    if msg == "reset_sent":
        messages.success(request, "Reset link sent to your email.")
    # ... (other messages)

    # 3. Handle Login Submission
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            role = get_role(user)
            if user.is_superuser or role in ["admin", "admin_manager"]:
                messages.error(request, "Please use the appropriate admin login.")
            elif role == "principal":
                login(request, user)
                return redirect("admin_console")
            else:
                messages.error(request, "You are not authorized to access this panel.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "admin_login.html")

# ── Manage Admins ────────────────────────────────────────────────────────────
@login_required(login_url="admin_login")
def manage_admins(request):
    role = get_role(request.user)
    if not request.user.is_superuser and role not in ("admin", "principal"):
        return HttpResponse("Unauthorized", status=403)

    superusers     = User.objects.filter(is_superuser=True)
    admin_managers = AdminManager.objects.select_related('user').all()

    if request.method == "POST" and "change_password" in request.POST:
        new_password = request.POST.get("new_password")
        if new_password:
            user = superusers.first()
            user.set_password(new_password)
            user.save()
            messages.success(request, "Superuser password updated successfully.")
        else:
            messages.error(request, "Password cannot be empty.")
        return redirect("manage_admins")

    return render(request, "manage_admins.html", {
        "superusers":     superusers,
        "admin_managers": admin_managers,
    })

def admin_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        User = get_user_model()
        users = User.objects.filter(email=email).filter(
            Q(is_superuser=True) | Q(role='admin') | Q(role='admin_manager')
        )
        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f'/reset/{uid}/{token}/'
            )
            send_mail(
                subject='Admin Portal — Password Reset',
                message=f'Click the link below to reset your password:\n\n{reset_link}\n\nThis link expires in 24 hours.',
                from_email=None,
                recipient_list=[email],
            )
        logout(request)
        return redirect('/admin-login/?msg=reset_sent')

    return render(request, 'password_reset.html')

# ── Add Admin Manager ────────────────────────────────────────────────────────
@login_required(login_url="admin_login")
def add_admin_manager(request):
    role = get_role(request.user)
    if not request.user.is_superuser and role not in ("admin", "principal"):
        return HttpResponse("Unauthorized", status=403)

    if request.method == "POST":
        form = AdminManagerForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data.get('email', ''),
                role='admin_manager',
                is_staff=True,
                school=getattr(request.user, 'school', None),
            )
            admin_mgr      = form.save(commit=False)
            admin_mgr.user = user
            admin_mgr.save()
            messages.success(request, f"Admin Manager '{admin_mgr.full_name}' created.")
            return redirect('manage_admins')
    else:
        form = AdminManagerForm()

    return render(request, 'accounts/admin_manager_form.html', {
        'form': form, 'action': 'Add',
    })


# ── Edit Admin Manager ───────────────────────────────────────────────────────
@login_required(login_url="admin_login")
def edit_admin_manager(request, pk):
    role = get_role(request.user)
    if not request.user.is_superuser and role not in ("admin", "principal"):
        return HttpResponse("Unauthorized", status=403)

    admin_mgr = get_object_or_404(AdminManager, pk=pk)

    if request.method == "POST":
        form = AdminManagerForm(request.POST, instance=admin_mgr,
                                instance_user=admin_mgr.user)
        if form.is_valid():
            user          = admin_mgr.user
            user.username = form.cleaned_data['username']
            user.email    = form.cleaned_data.get('email', '')
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            form.save()
            messages.success(request, "Admin Manager updated.")
            return redirect('manage_admins')
    else:
        form = AdminManagerForm(instance=admin_mgr,
                                instance_user=admin_mgr.user)

    return render(request, 'accounts/admin_manager_form.html', {
        'form': form, 'action': 'Edit',
    })


# ── Delete Admin Manager ─────────────────────────────────────────────────────
@login_required(login_url="admin_login")
def delete_admin_manager(request, pk):
    role = get_role(request.user)
    if not request.user.is_superuser and role not in ("admin", "principal"):
        return HttpResponse("Unauthorized", status=403)

    admin_mgr = get_object_or_404(AdminManager, pk=pk)
    user      = admin_mgr.user
    name      = admin_mgr.full_name
    admin_mgr.delete()
    user.delete()
    messages.success(request, f"Admin Manager '{name}' deleted.")
    return redirect('manage_admins')

from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect

def student_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        users = User.objects.filter(email=email, role='student')

        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f'/accounts/student/reset/{uid}/{token}/'
            )
            send_mail(
                subject='Student Password Reset',
                message=f'Click the link to reset your password: {reset_link}',
                from_email='nafiaaziz.500@gmail.com',
                recipient_list=[email],
            )

        return redirect('/student/password-reset/?msg=sent')

    return render(request, 'student_password_reset.html')


def parent_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        users = User.objects.filter(email=email, role='parent')

        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f'/accounts/parent/reset/{uid}/{token}/'
            )
            send_mail(
                subject='Parent Password Reset',
                message=f'Click the link to reset your password: {reset_link}',
                from_email='nafiaaziz.500@gmail.com',
                recipient_list=[email],
            )

        return redirect('/parent/password-reset/?msg=sent')

    return render(request, 'parent_password_reset.html')
