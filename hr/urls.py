from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employee_list, name='hr_employee_list'),
    path('salary-config/', views.salary_config, name='hr_salary_config'),
    path('employee/<int:employee_id>/salary/add/', views.add_employee_salary, name='hr_add_employee_salary'),
    path('employee/<int:employee_id>/salary/edit/', views.edit_employee_salary, name='hr_edit_employee_salary'),
    path('salary/generate/', views.generate_monthly_salary, name='hr_generate_salary'),
    path('salary/monthly/', views.monthly_salary_list, name='hr_monthly_salary_list'),
    path('salary/<int:pk>/edit/', views.edit_monthly_salary, name='hr_edit_monthly_salary'),
    path('salary/<int:pk>/slip/', views.salary_slip, name='hr_salary_slip'),
    path('salary/<int:pk>/slip/pdf/', views.salary_slip_pdf, name='hr_salary_slip_pdf'),
    path('salary/slip/all/', views.salary_slip_all, name='hr_salary_slip_all'),
    path('attendance/', views.employee_attendance, name='hr_employee_attendance'),
]
