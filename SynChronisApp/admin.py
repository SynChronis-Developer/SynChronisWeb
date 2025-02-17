from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(LoginTable)
admin.site.register(TeacherTable)
admin.site.register(StudentTable)
admin.site.register(ClassTable)
admin.site.register(SubjectsTable)
admin.site.register(SemesterTable)
admin.site.register(AttendanceTable)
admin.site.register(LocationTable)
admin.site.register(TimeTableTable)
admin.site.register(NotesTable)
admin.site.register(LeaveApplicationTable)
admin.site.register(StudentNoticeTable)
admin.site.register(TeacherNoticeTable)
admin.site.register(DepartmentsTable)
admin.site.register(CourseTable)
admin.site.register(CollegeDetailsTable)
admin.site.register(PasswordResetOTP)
admin.site.register(RegistrationOTP)
