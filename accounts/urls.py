from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin-login/", views.admin_login, name="admin_login"),
    path('manage-admins/', views.manage_admins, name='manage_admins'),
    path('manage-admins/add/', views.add_admin_manager, name='add_admin_manager'),                      # ← add
    path('manage-admins/edit/<int:pk>/', views.edit_admin_manager, name='edit_admin_manager'),          # ← add
    path('manage-admins/delete/<int:pk>/', views.delete_admin_manager, name='delete_admin_manager'),    # ← add

   path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        success_url='/admin-login/?msg=reset_sent'
    ), name='password_reset'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/admin-login/?msg=reset_done'
    ), name='password_reset_confirm'),

    path('password-change/', views.admin_password_reset, name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='admin_login.html'
    ), name='password_change_done'),


# ── ADD THESE to urlpatterns in urls.py ──────────────────────────────────────

    # Student password reset
    path('student/password-reset/', views.student_password_reset, name='student_password_reset'),

    path('accounts/student/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/student/login/?msg=reset_done'
    ), name='student_password_reset_confirm'),

    path('accounts/student-password-change/', auth_views.PasswordChangeView.as_view(
        template_name='password_reset.html',
        success_url='/student/login/?msg=reset_done'
    ), name='student_password_change'),
    # ── ADD THESE to urlpatterns in urls.py ──────────────────────────────────────

    # Parent password reset
    path('parent/password-reset/', views.parent_password_reset, name='parent_password_reset'),

    path('accounts/parent/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/parent/login/?msg=reset_done'
    ), name='parent_password_reset_confirm'),

    path('accounts/parent-password-change/', auth_views.PasswordChangeView.as_view(
        template_name='password_reset.html',
        success_url='/parent/login/?msg=reset_done'
    ), name='parent_password_change'),
]
