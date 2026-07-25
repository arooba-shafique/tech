from django.contrib import admin
from .models import SalaryConfig, EmployeeSalary, MonthlySalary, EmployeeAttendance

admin.site.register(SalaryConfig)
admin.site.register(EmployeeSalary)
admin.site.register(MonthlySalary)
admin.site.register(EmployeeAttendance)
