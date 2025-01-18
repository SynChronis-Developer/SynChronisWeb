from django.contrib import admin
from .models import BatchTable, CourseTable, DepartmentsTable, LeaveApplicationTable, LocationTable, LoginTable, NotesTable, SemesterTable, StudentNoticeTable, SubjectsTable, TeacherNoticeTable, TimeTableTable
from .models import TeacherTable
from .models import StudentTable
from .models import ClassTable
from .models import AttendanceTable

# Register your models here.
admin.site.register(LoginTable)
admin.site.register(TeacherTable)
admin.site.register(StudentTable)
admin.site.register(ClassTable)
admin.site.register(SubjectsTable)
admin.site.register(BatchTable)
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
