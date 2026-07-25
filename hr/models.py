from django.db import models
from django.conf import settings
from academics.models import TeacherProfile
import calendar


class SalaryConfig(models.Model):
    """Global salary configuration per school."""
    school = models.OneToOneField('accounts.School', on_delete=models.CASCADE, related_name='salary_config', null=True, blank=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Tax percentage deducted from gross salary")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Salary Config - {self.school}"


class EmployeeSalary(models.Model):
    """Salary structure for each employee (teacher)."""
    SALARY_TYPE_CHOICES = (
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
    )
    EMPLOYMENT_TYPE_CHOICES = (
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('daily_wager', 'Daily Wager'),
    )

    employee = models.OneToOneField(TeacherProfile, on_delete=models.CASCADE, related_name='salary_detail')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salary_type = models.CharField(max_length=10, choices=SALARY_TYPE_CHOICES, default='monthly')
    employment_type = models.CharField(max_length=15, choices=EMPLOYMENT_TYPE_CHOICES, default='permanent')
    working_days_per_week = models.PositiveIntegerField(default=6)
    bank_account = models.CharField(max_length=50, blank=True, default='')
    bank_name = models.CharField(max_length=100, blank=True, default='')

    # Allowances
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fuel_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_allowances(self):
        return (self.housing_allowance + self.medical_allowance +
                self.transport_allowance + self.fuel_allowance + self.other_allowance)

    def __str__(self):
        return f"{self.employee.full_name} - {self.basic_salary}"


class MonthlySalary(models.Model):
    """Monthly salary record for each employee."""
    PAY_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
    )

    employee = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='monthly_salaries')
    salary_config = models.ForeignKey(SalaryConfig, on_delete=models.SET_NULL, null=True, blank=True)
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()

    # Attendance
    total_working_days = models.PositiveIntegerField(default=26)
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)
    allowed_leaves = models.PositiveIntegerField(default=0)
    late_coming_days = models.PositiveIntegerField(default=0)

    # Salary breakdown
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    increment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    per_day_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Allowances
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fuel_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Deductions
    leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    late_coming_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    security_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Bonus
    bonus_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Bonus per day if no leaves taken")
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Totals
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Status
    pay_status = models.CharField(max_length=10, choices=PAY_STATUS_CHOICES, default='unpaid')
    payment_date = models.DateField(null=True, blank=True)

    # Remarks
    remarks = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')
        ordering = ['-year', '-month']

    def calculate_salary(self):
        """Auto-calculate salary based on config and attendance."""
        emp_salary = EmployeeSalary.objects.filter(employee=self.employee).first()
        if not emp_salary:
            return

        self.basic_salary = emp_salary.basic_salary
        self.housing_allowance = emp_salary.housing_allowance
        self.medical_allowance = emp_salary.medical_allowance
        self.transport_allowance = emp_salary.transport_allowance
        self.fuel_allowance = emp_salary.fuel_allowance
        self.other_allowance = emp_salary.other_allowance

        # Calculate per day salary
        if self.total_working_days > 0:
            self.per_day_salary = self.basic_salary / self.total_working_days

        # Leave deduction (absent days beyond allowed leaves)
        excess_absent = max(0, self.days_absent - self.allowed_leaves)
        self.leave_deduction = excess_absent * self.per_day_salary

        # Late coming deduction (e.g. half day per 3 lates)
        self.late_coming_deduction = (self.late_coming_days // 3) * (self.per_day_salary / 2)

        # Bonus: if no absent days (0 leaves in whole month)
        if self.days_absent == 0 and self.allowed_leaves == 0:
            self.bonus_amount = self.bonus_per_day * self.total_working_days
        else:
            self.bonus_amount = 0

        # Tax deduction
        salary_config = self.salary_config or SalaryConfig.objects.first()
        if salary_config:
            tax_pct = salary_config.tax_percentage
        else:
            tax_pct = 0

        total_allowances = (self.housing_allowance + self.medical_allowance +
                          self.transport_allowance + self.fuel_allowance + self.other_allowance)

        # Gross salary
        self.gross_salary = (self.basic_salary + self.increment + total_allowances +
                           self.bonus_amount - self.leave_deduction - self.late_coming_deduction)

        # Tax on gross
        self.tax_deduction = self.gross_salary * (tax_pct / 100)

        # Total deductions
        self.total_deductions = (self.leave_deduction + self.late_coming_deduction +
                               self.advance_deduction + self.provident_fund +
                               self.security_deduction + self.tax_deduction + self.other_deduction)

        # Net salary
        self.net_salary = self.gross_salary - self.total_deductions

    def save(self, *args, **kwargs):
        self.calculate_salary()
        super().save(*args, **kwargs)

    @property
    def total_allowances(self):
        return (self.housing_allowance + self.medical_allowance +
                self.transport_allowance + self.fuel_allowance + self.other_allowance)

    def __str__(self):
        month_name = calendar.month_name[self.month]
        return f"{self.employee.full_name} - {month_name} {self.year} - {self.net_salary}"


class EmployeeAttendance(models.Model):
    """Daily attendance tracking for employees."""
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
        ('half_day', 'Half Day'),
        ('late', 'Late'),
    )

    employee = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='employee_attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.get_status_display()})"
