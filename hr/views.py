import calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
import json

from academics.models import TeacherProfile
from .models import EmployeeSalary, MonthlySalary, SalaryConfig, EmployeeAttendance
from .forms import (
    EmployeeSalaryForm, MonthlySalaryForm, SalaryConfigForm,
    EmployeeAttendanceForm, GenerateSalaryForm
)


def get_user_school(user):
    return getattr(user, 'school', None)


# ─────────────────────────────────────────────
# EMPLOYEE (TEACHER) HR VIEW — with all FORMAT.xlsx fields
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def employee_list(request):
    """Employee list matching FORMAT.xlsx columns."""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    school = get_user_school(request.user)
    employees = TeacherProfile.objects.select_related('salary_detail').all()
    if school and not request.user.is_superuser:
        employees = employees.filter(school=school)

    # Attach salary info
    for emp in employees:
        sal = getattr(emp, 'salary_detail', None)
        emp.basic_salary = sal.basic_salary if sal else 0
        emp.salary_type = sal.get_salary_type_display() if sal else '-'
        emp.employment_type = sal.get_employment_type_display() if sal else '-'
        emp.working_days = f"{sal.working_days_per_week}/week" if sal else '-'

    context = {
        'employees': employees,
        'section': 'employees',
    }
    return render(request, 'hr/employee_list.html', context)


# ─────────────────────────────────────────────
# SALARY CONFIG
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def salary_config(request):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    config = SalaryConfig.objects.first()
    if not config:
        config = SalaryConfig.objects.create(tax_percentage=0)

    if request.method == 'POST':
        config.default_working_days = int(request.POST.get('default_working_days', 26))
        config.max_allowed_leaves = int(request.POST.get('max_allowed_leaves', 0))
        config.late_deduction_per = int(request.POST.get('late_deduction_per', 3))
        config.tax_percentage = float(request.POST.get('tax_percentage', 0))
        config.provident_fund_pct = float(request.POST.get('provident_fund_pct', 0))
        config.housing_allowance_pct = float(request.POST.get('housing_allowance_pct', 0))
        config.medical_allowance_pct = float(request.POST.get('medical_allowance_pct', 0))
        config.transport_allowance_pct = float(request.POST.get('transport_allowance_pct', 0))
        config.fuel_allowance_pct = float(request.POST.get('fuel_allowance_pct', 0))
        config.bonus_per_day = float(request.POST.get('bonus_per_day', 0))
        config.bonus_percentage = float(request.POST.get('bonus_percentage', 0))
        config.save()
        messages.success(request, 'Salary configuration updated.')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('admin_dashboard')

    return render(request, 'hr/salary_config.html', {'config': config, 'section': 'config'})


# ─────────────────────────────────────────────
# EMPLOYEE SALARY STRUCTURE (Add/Edit)
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def add_employee_salary(request, employee_id):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    employee = get_object_or_404(TeacherProfile, pk=employee_id)
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST)
        if form.is_valid():
            sal = form.save(commit=False)
            sal.employee = employee
            sal.save()
            messages.success(request, f'Salary structure saved for {employee.full_name}.')
            return redirect('hr_employee_list')
    else:
        form = EmployeeSalaryForm(initial={'employee': employee})
    return render(request, 'hr/employee_salary_form.html', {
        'form': form, 'employee': employee, 'action': 'Add'
    })


@login_required(login_url='admin_login')
def edit_employee_salary(request, employee_id):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    employee = get_object_or_404(TeacherProfile, pk=employee_id)
    sal, created = EmployeeSalary.objects.get_or_create(employee=employee)

    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST, instance=sal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Salary structure updated for {employee.full_name}.')
            return redirect('hr_employee_list')
    else:
        form = EmployeeSalaryForm(instance=sal)
    return render(request, 'hr/employee_salary_form.html', {
        'form': form, 'employee': employee, 'action': 'Edit'
    })


# ─────────────────────────────────────────────
# GENERATE MONTHLY SALARY — Bulk
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def generate_monthly_salary(request):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    school = get_user_school(request.user)
    employees = TeacherProfile.objects.all()
    if school and not request.user.is_superuser:
        employees = employees.filter(school=school)

    if request.method == 'POST':
        month = int(request.POST.get('month', timezone.now().month))
        year = int(request.POST.get('year', timezone.now().year))
        total_working_days = int(request.POST.get('total_working_days', 26))
        bonus_per_day = request.POST.get('bonus_per_day', '0')
        bonus_per_day = float(bonus_per_day) if bonus_per_day else 0

        created_count = 0
        updated_count = 0

        for emp in employees:
            # Use teacher's salary from profile directly
            emp_salary, _ = EmployeeSalary.objects.get_or_create(
                employee=emp,
                defaults={'basic_salary': emp.salary}
            )
            if emp.salary > 0 and emp_salary.basic_salary != emp.salary:
                emp_salary.basic_salary = emp.salary
                emp_salary.save()

            # Get attendance data for this month
            att_records = EmployeeAttendance.objects.filter(
                employee=emp,
                date__year=year,
                date__month=month
            )
            days_present = att_records.filter(status__in=['present', 'late']).count()
            days_absent = att_records.filter(status='absent').count()
            late_days = att_records.filter(status='late').count()
            leave_days = att_records.filter(status='leave').count()

            monthly, created = MonthlySalary.objects.get_or_create(
                employee=emp, month=month, year=year,
                defaults={
                    'salary_config': SalaryConfig.objects.first(),
                    'total_working_days': total_working_days,
                    'days_present': days_present,
                    'days_absent': days_absent,
                    'allowed_leaves': leave_days,
                    'late_coming_days': late_days,
                    'basic_salary': emp.salary,
                    'increment': 0,
                    'bonus_per_day': bonus_per_day,
                }
            )
            if created:
                created_count += 1
            else:
                monthly.total_working_days = total_working_days
                monthly.days_present = days_present
                monthly.days_absent = days_absent
                monthly.allowed_leaves = leave_days
                monthly.late_coming_days = late_days
                monthly.basic_salary = emp.salary
                monthly.bonus_per_day = bonus_per_day
                monthly.salary_config = SalaryConfig.objects.first()
                monthly.save()
                updated_count += 1

        month_name = calendar.month_name[month]
        messages.success(request, f'Salary generated for {month_name} {year}: {created_count} new, {updated_count} updated.')
        return redirect('hr_monthly_salary_list')

    form = GenerateSalaryForm(initial={
        'month': timezone.now().month,
        'year': timezone.now().year,
        'total_working_days': 26,
        'bonus_per_day': 0,
    })
    return render(request, 'hr/generate_salary.html', {'form': form})


# ─────────────────────────────────────────────
# MONTHLY SALARY LIST
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def monthly_salary_list(request):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        month = timezone.now().month
        year = timezone.now().year

    salaries = MonthlySalary.objects.filter(month=month, year=year).select_related('employee')
    month_name = calendar.month_name[month]

    # Totals
    total_gross = sum(s.gross_salary for s in salaries)
    total_deductions = sum(s.total_deductions for s in salaries)
    total_net = sum(s.net_salary for s in salaries)

    context = {
        'salaries': salaries,
        'month': month,
        'year': year,
        'month_name': month_name,
        'total_gross': total_gross,
        'total_deductions': total_deductions,
        'total_net': total_net,
    }
    return render(request, 'hr/monthly_salary_list.html', context)


# ─────────────────────────────────────────────
# EDIT MONTHLY SALARY
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def edit_monthly_salary(request, pk):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    salary = get_object_or_404(MonthlySalary, pk=pk)

    if request.method == 'POST':
        salary.days_present = int(request.POST.get('days_present', salary.days_present))
        salary.days_absent = int(request.POST.get('days_absent', salary.days_absent))
        salary.allowed_leaves = int(request.POST.get('allowed_leaves', salary.allowed_leaves))
        salary.late_coming_days = int(request.POST.get('late_coming_days', salary.late_coming_days))
        salary.increment = float(request.POST.get('increment', salary.increment))
        salary.advance_deduction = float(request.POST.get('advance_deduction', salary.advance_deduction))
        salary.provident_fund = float(request.POST.get('provident_fund', salary.provident_fund))
        salary.security_deduction = float(request.POST.get('security_deduction', salary.security_deduction))
        salary.other_deduction = float(request.POST.get('other_deduction', salary.other_deduction))
        salary.remarks = request.POST.get('remarks', salary.remarks)
        salary.pay_status = request.POST.get('pay_status', salary.pay_status)
        salary.save()
        messages.success(request, f'Salary updated for {salary.employee.full_name}.')
        return redirect('hr_monthly_salary_list')

    return render(request, 'hr/edit_monthly_salary.html', {'salary': salary})


# ─────────────────────────────────────────────
# SALARY SLIP PDF (HTML-based for download)
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def salary_slip(request, pk):
    salary = get_object_or_404(MonthlySalary, pk=pk)
    employee = salary.employee
    emp_salary = EmployeeSalary.objects.filter(employee=employee).first()
    month_name = calendar.month_name[salary.month]

    context = {
        'salary': salary,
        'employee': employee,
        'emp_salary': emp_salary,
        'month_name': month_name,
    }
    return render(request, 'hr/salary_slip.html', context)


@login_required(login_url='admin_login')
def salary_slip_pdf(request, pk):
    """Returns a printable salary slip page for PDF generation."""
    salary = get_object_or_404(MonthlySalary, pk=pk)
    employee = salary.employee
    emp_salary = EmployeeSalary.objects.filter(employee=employee).first()
    month_name = calendar.month_name[salary.month]

    context = {
        'salary': salary,
        'employee': employee,
        'emp_salary': emp_salary,
        'month_name': month_name,
        'print_mode': True,
    }
    return render(request, 'hr/salary_slip_print.html', context)


@login_required(login_url='admin_login')
def salary_slip_all(request):
    """Print all salary slips for a given month/year."""
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))

    salaries = MonthlySalary.objects.filter(month=month, year=year).select_related('employee')
    month_name = calendar.month_name[month]

    context = {
        'salaries': salaries,
        'month_name': month_name,
        'year': year,
        'print_all': True,
    }
    return render(request, 'hr/salary_slip_print_all.html', context)


# ─────────────────────────────────────────────
# EMPLOYEE ATTENDANCE
# ─────────────────────────────────────────────

@login_required(login_url='admin_login')
def employee_attendance(request):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ('admin', 'admin_manager')):
        return HttpResponse("Unauthorized", status=403)

    school = get_user_school(request.user)
    employees = TeacherProfile.objects.all()
    if school and not request.user.is_superuser:
        employees = employees.filter(school=school)

    today = timezone.now().date()
    selected_date = request.GET.get('date', str(today))
    try:
        from datetime import date as dt_date
        att_date = dt_date.fromisoformat(selected_date)
    except ValueError:
        att_date = today

    # Get or create attendance records for the selected date
    existing = {
        att.employee_id: att
        for att in EmployeeAttendance.objects.filter(date=att_date)
    }

    if request.method == 'POST':
        for emp in employees:
            status = request.POST.get(f'status_{emp.id}', 'present')
            check_in = request.POST.get(f'check_in_{emp.id}', '')
            check_out = request.POST.get(f'check_out_{emp.id}', '')
            remarks = request.POST.get(f'remarks_{emp.id}', '')

            att, created = EmployeeAttendance.objects.update_or_create(
                employee=emp, date=att_date,
                defaults={
                    'status': status,
                    'check_in': check_in if check_in else None,
                    'check_out': check_out if check_out else None,
                    'remarks': remarks,
                }
            )
        messages.success(request, f'Attendance saved for {att_date}.')
        return redirect(f'/hr/attendance/?date={att_date}')

    context = {
        'employees': employees,
        'selected_date': att_date,
        'existing': existing,
    }
    return render(request, 'hr/employee_attendance.html', context)
