import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dps_ravi.settings')

import django
django.setup()

from decimal import Decimal

from accounts.models import User, School
from academics.models import TeacherProfile
from hr.models import SalaryConfig, EmployeeSalary, MonthlySalary, EmployeeAttendance
from datetime import date, time
import calendar

print("Creating dummy data...")

# 1. School
school, _ = School.objects.get_or_create(name='Royal International School System', defaults={'is_active': True})
print(f"School: {school.name}")

# 2. Admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'role': 'admin',
        'is_active': True,
        'is_staff': True,
        'is_superuser': True,
        'school': school,
        'first_name': 'Admin',
        'last_name': 'User',
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
print(f"Admin: {admin_user.username}")

# 3. HR Manager
hr_user, created = User.objects.get_or_create(
    username='hr_manager',
    defaults={
        'role': 'admin_manager',
        'is_active': True,
        'is_staff': True,
        'is_superuser': False,
        'school': school,
        'first_name': 'HR',
        'last_name': 'Manager',
    }
)
if created:
    hr_user.set_password('admin123')
    hr_user.save()
print(f"HR Manager: {hr_user.username}")

# 4. Teachers/Staff
employees_data = [
    {
        'username': 'ahmed_khan', 'full_name': 'Ahmed Khan', 'father_name': 'Rashid Khan',
        'gender': 'M', 'employee_id': 'EMP001', 'cnic': '35202-1234567-1',
        'designation': 'teacher', 'employment_type': 'permanent',
        'joining_date': date(2020, 3, 1), 'phone': '0301-1234567',
        'address': 'Lahore, Punjab', 'email': 'ahmed.khan@school.edu',
        'salary': Decimal('50000'), 'date_of_birth': date(1990, 5, 15),
    },
    {
        'username': 'fatima.ali', 'full_name': 'Fatima Ali', 'father_name': 'Ali Mohammad',
        'gender': 'F', 'employee_id': 'EMP002', 'cnic': '35202-2345678-2',
        'designation': 'coordinator', 'employment_type': 'permanent',
        'joining_date': date(2019, 7, 15), 'phone': '0321-2345678',
        'address': 'Lahore, Punjab', 'email': 'fatima.ali@school.edu',
        'salary': Decimal('55000'), 'date_of_birth': date(1992, 8, 20),
    },
    {
        'username': 'hassan.raza', 'full_name': 'Muhammad Hassan', 'father_name': 'Hassan Raza',
        'gender': 'M', 'employee_id': 'EMP003', 'cnic': '35202-3456789-3',
        'designation': 'teacher', 'employment_type': 'permanent',
        'joining_date': date(2021, 1, 10), 'phone': '0333-3456789',
        'address': 'Lahore, Punjab', 'email': 'hassan@school.edu',
        'salary': Decimal('48000'), 'date_of_birth': date(1988, 12, 10),
    },
    {
        'username': 'ayesha.malik', 'full_name': 'Ayesha Malik', 'father_name': 'Malik Tariq',
        'gender': 'F', 'employee_id': 'EMP004', 'cnic': '35202-4567890-4',
        'designation': 'teacher', 'employment_type': 'contract',
        'joining_date': date(2022, 6, 1), 'phone': '0345-4567890',
        'address': 'Lahore, Punjab', 'email': 'ayesha@school.edu',
        'salary': Decimal('42000'), 'date_of_birth': date(1995, 3, 25),
    },
    {
        'username': 'usman.ahmed', 'full_name': 'Usman Ahmed', 'father_name': 'Ahmed Nawaz',
        'gender': 'M', 'employee_id': 'EMP005', 'cnic': '35202-5678901-5',
        'designation': 'manager', 'employment_type': 'permanent',
        'joining_date': date(2018, 9, 1), 'phone': '0300-5678901',
        'address': 'Lahore, Punjab', 'email': 'usman@school.edu',
        'salary': Decimal('65000'), 'date_of_birth': date(1991, 11, 30),
    },
    {
        'username': 'sara.raza', 'full_name': 'Sara Raza', 'father_name': 'Raza Ali',
        'gender': 'F', 'employee_id': 'EMP006', 'cnic': '35202-6789012-6',
        'designation': 'teacher', 'employment_type': 'permanent',
        'joining_date': date(2021, 4, 15), 'phone': '0311-6789012',
        'address': 'Lahore, Punjab', 'email': 'sara@school.edu',
        'salary': Decimal('47000'), 'date_of_birth': date(1993, 7, 18),
    },
    {
        'username': 'bilal.siddiqui', 'full_name': 'Bilal Siddiqui', 'father_name': 'Siddiqui Ahmad',
        'gender': 'M', 'employee_id': 'EMP007', 'cnic': '35202-7890123-7',
        'designation': 'vp', 'employment_type': 'permanent',
        'joining_date': date(2017, 2, 1), 'phone': '0322-7890123',
        'address': 'Lahore, Punjab', 'email': 'bilal@school.edu',
        'salary': Decimal('75000'), 'date_of_birth': date(1989, 1, 5),
    },
    {
        'username': 'zainab.iqbal', 'full_name': 'Zainab Iqbal', 'father_name': 'Iqbal Hussain',
        'gender': 'F', 'employee_id': 'EMP008', 'cnic': '35202-8901234-8',
        'designation': 'teacher', 'employment_type': 'daily_wager',
        'joining_date': date(2023, 1, 15), 'phone': '0333-8901234',
        'address': 'Lahore, Punjab', 'email': 'zainab@school.edu',
        'salary': Decimal('25000'), 'date_of_birth': date(1994, 9, 12),
    },
]

bank_data = [
    ('HBL', '1234567890'),
    ('UBL', '2345678901'),
    ('MCB', '3456789012'),
    ('ALLIED', '4567890123'),
    ('NBP', '5678901234'),
    ('FAYSAL', '6789012345'),
    ('HBL', '7890123456'),
    ('', ''),
]

teachers = []
for i, data in enumerate(employees_data):
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'role': 'teacher',
            'is_active': True,
            'school': school,
            'first_name': data['full_name'].split()[0],
            'last_name': ' '.join(data['full_name'].split()[1:]),
        }
    )
    if created:
        user.set_password('teacher123')
        user.save()

    tp, _ = TeacherProfile.objects.get_or_create(
        user=user,
        defaults={
            'school': school,
            'full_name': data['full_name'],
            'father_name': data['father_name'],
            'date_of_birth': data['date_of_birth'],
            'gender': data['gender'],
            'employee_id': data['employee_id'],
            'cnic': data['cnic'],
            'designation': data['designation'],
            'employment_type': data['employment_type'],
            'skill_level': 'permanent_professional',
            'joining_date': data['joining_date'],
            'phone': data['phone'],
            'address': data['address'],
            'email': data['email'],
            'salary': data['salary'],
            'salary_type': 'monthly',
            'working_days_per_week': 6,
            'bank_account': bank_data[i][1],
            'bank_name': bank_data[i][0],
        }
    )
    teachers.append(tp)
    print(f"Teacher: {tp.full_name} ({tp.employee_id})")

# 5. Salary Config
config, _ = SalaryConfig.objects.get_or_create(
    school=school,
    defaults={
        'default_working_days': 26,
        'tax_percentage': Decimal('2.00'),
        'housing_allowance_pct': Decimal('10.00'),
        'medical_allowance_pct': Decimal('5.00'),
        'transport_allowance_pct': Decimal('5.00'),
        'fuel_allowance_pct': Decimal('3.00'),
        'bonus_per_day': Decimal('500.00'),
        'bonus_percentage': Decimal('0'),
        'provident_fund_pct': Decimal('0'),
        'max_allowed_leaves': 1,
        'late_deduction_per': 3,
    }
)
print(f"Salary Config created")

# 6. Employee Salary Structures
salary_data = [
    (Decimal('50000'), Decimal('5000'), Decimal('2500'), Decimal('2500'), Decimal('1500'), Decimal('0')),
    (Decimal('55000'), Decimal('5500'), Decimal('2750'), Decimal('2750'), Decimal('1650'), Decimal('0')),
    (Decimal('48000'), Decimal('4800'), Decimal('2400'), Decimal('2400'), Decimal('1440'), Decimal('0')),
    (Decimal('42000'), Decimal('4200'), Decimal('2100'), Decimal('2100'), Decimal('1260'), Decimal('0')),
    (Decimal('65000'), Decimal('6500'), Decimal('3250'), Decimal('3250'), Decimal('1950'), Decimal('0')),
    (Decimal('47000'), Decimal('4700'), Decimal('2350'), Decimal('2350'), Decimal('1410'), Decimal('0')),
    (Decimal('75000'), Decimal('7500'), Decimal('3750'), Decimal('3750'), Decimal('2250'), Decimal('0')),
    (Decimal('25000'), Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0')),
]

for i, tp in enumerate(teachers):
    sal_type = 'daily' if tp.employment_type == 'daily_wager' else 'monthly'
    emp_sal, _ = EmployeeSalary.objects.get_or_create(
        employee=tp,
        defaults={
            'basic_salary': salary_data[i][0],
            'salary_type': sal_type,
            'employment_type': tp.employment_type,
            'working_days_per_week': 6,
            'bank_account': bank_data[i][1],
            'bank_name': bank_data[i][0],
            'housing_allowance': salary_data[i][1],
            'medical_allowance': salary_data[i][2],
            'transport_allowance': salary_data[i][3],
            'fuel_allowance': salary_data[i][4],
            'other_allowance': salary_data[i][5],
        }
    )
print(f"Employee salaries created")

# 7. Monthly Salaries (July 2026)
monthly_data = [
    {'days_absent': 2, 'paid_leaves': 0, 'unpaid_leaves': 1, 'late_coming_days': 2, 'pay_status': 'paid', 'remarks': 'July salary'},
    {'days_absent': 0, 'paid_leaves': 1, 'unpaid_leaves': 0, 'late_coming_days': 1, 'pay_status': 'paid', 'remarks': 'July salary'},
    {'days_absent': 3, 'paid_leaves': 0, 'unpaid_leaves': 3, 'late_coming_days': 4, 'pay_status': 'unpaid', 'remarks': '3 unpaid leaves'},
    {'days_absent': 1, 'paid_leaves': 0, 'unpaid_leaves': 0, 'late_coming_days': 0, 'pay_status': 'paid', 'remarks': 'July salary'},
    {'days_absent': 0, 'paid_leaves': 0, 'unpaid_leaves': 0, 'late_coming_days': 1, 'pay_status': 'paid', 'remarks': 'July salary'},
    {'days_absent': 2, 'paid_leaves': 1, 'unpaid_leaves': 0, 'late_coming_days': 3, 'pay_status': 'paid', 'remarks': 'July salary'},
    {'days_absent': 0, 'paid_leaves': 0, 'unpaid_leaves': 0, 'late_coming_days': 0, 'pay_status': 'paid', 'remarks': 'July salary'},
    {'days_absent': 4, 'paid_leaves': 0, 'unpaid_leaves': 2, 'late_coming_days': 5, 'pay_status': 'unpaid', 'remarks': 'Daily wager - 4 absents'},
]

for i, tp in enumerate(teachers):
    ms, created = MonthlySalary.objects.get_or_create(
        employee=tp, month=7, year=2026,
        defaults={
            'salary_config': config,
            'total_working_days': 26,
            'days_absent': monthly_data[i]['days_absent'],
            'paid_leaves': monthly_data[i]['paid_leaves'],
            'unpaid_leaves': monthly_data[i]['unpaid_leaves'],
            'late_coming_days': monthly_data[i]['late_coming_days'],
            'basic_salary': tp.salary,
            'pay_status': monthly_data[i]['pay_status'],
            'remarks': monthly_data[i]['remarks'],
        }
    )
    if created:
        print(f"July salary: {tp.full_name} - Net: {ms.net_salary}")

# Also create June 2026 for some employees
june_data = [
    (teachers[0], 1, 0, 0, 1, 'paid', 'June salary'),
    (teachers[1], 0, 0, 0, 0, 'paid', 'June salary'),
    (teachers[2], 2, 0, 0, 2, 'paid', 'June salary'),
    (teachers[4], 0, 0, 0, 0, 'paid', 'June salary'),
    (teachers[6], 0, 0, 0, 0, 'paid', 'June salary'),
]

for tp, absent, paid, unpaid, late, status, remarks in june_data:
    ms, created = MonthlySalary.objects.get_or_create(
        employee=tp, month=6, year=2026,
        defaults={
            'salary_config': config,
            'total_working_days': 26,
            'days_absent': absent,
            'paid_leaves': paid,
            'unpaid_leaves': unpaid,
            'late_coming_days': late,
            'basic_salary': tp.salary,
            'pay_status': status,
            'remarks': remarks,
        }
    )
    if created:
        print(f"June salary: {tp.full_name} - Net: {ms.net_salary}")

print("\nDone! All dummy data created.")
print(f"Total users: {User.objects.count()}")
print(f"Total teachers: {TeacherProfile.objects.count()}")
print(f"Total salary configs: {SalaryConfig.objects.count()}")
print(f"Total employee salaries: {EmployeeSalary.objects.count()}")
print(f"Total monthly salaries: {MonthlySalary.objects.count()}")
