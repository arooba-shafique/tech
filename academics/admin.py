from django.contrib import admin
from .models import (
    Class,
    Subject,
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    TeacherSubjectAssignment,
    Attendance,
    Exam,
    Result,
    TimetableSlot
)

# Register all academic models
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(ParentProfile)
admin.site.register(TeacherSubjectAssignment)
admin.site.register(Attendance)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(TimetableSlot)