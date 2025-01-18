from django import views
from django.urls import path
from .views import (
    AcceptTeacher, AddDepartmentCourseView, AddStudentNoticeView, AddSubjectView, AddTeacherNoticeView,  Addnotes, AdminDashboard,
    AdminNotificationControl, ApproveLeaveApplication, AttendanceView, BatchView, CollegeDetailsView, 
    CreateBatchView,CreateSemesterView, CreateStudentNoticeView, CreateTeacherNoticeView, DeleteBatchView, DeleteEntryView,
    DeleteSemesterView, DeleteStudentNoticeView, DeleteTeacherNoticeView, DeleteTimeTableView,Location, LoginPage, 
    MainPage, ManageSemestersView, RejectTeacher,SendLeaveApplication,
    SetTimeTableView, StudentNoticeView, TeacherNoticeView,   TimetableView, UpdateBatchView,
    UpdateSemesterView, UpdateStudentNoticeView, UpdateTeacherNoticeView, UpdateTimeTableView, ViewNotes, ViewTeacher, ViewTimeTableView, 
)


urlpatterns = [
    path('', MainPage.as_view(), name='Main_Page'),
    path('Login_page/', LoginPage.as_view(), name='login'),
    path('View_Teacher/', ViewTeacher.as_view(), name='View_Teacher'),
    path('Admin_Dashboard/', AdminDashboard.as_view(), name='Admin_Dashboard'),
    path('Location/', Location.as_view(), name='Location'),
    path('accept_teacher/<int:id>/', AcceptTeacher.as_view(), name='accept_teacher'),
    path('reject_teacher/<int:id>/', RejectTeacher.as_view(), name='reject_teacher'),
    
    path('Send_Leave_Application/', SendLeaveApplication.as_view(), name='Leave_Application'),
    
    path('View_Leave_Application/', ApproveLeaveApplication.as_view(), name='View_Leave_Application'),
    # URL pattern for adding teacher notice
    path('Add_Notice_Teacher/',AddTeacherNoticeView.as_view(), name='add_teacher_notice'),
    
    # URL pattern for adding student notice
    path('Add_Notice_Student/', AddStudentNoticeView.as_view(), name='add_student_notice'),
    
    # Other URLs...
    path('Add_Note/', Addnotes.as_view(), name='Add_Note'),
    path('View_Notes/', ViewNotes.as_view(), name='View_Notes'),
    path('Admin_Notification_Control/', AdminNotificationControl.as_view(), name='Admin_Notification_Control'),
    path('manage_batches/', BatchView.as_view(), name='manage_batches'),
    path('create_batch/', CreateBatchView.as_view(), name='create_batch'),
    path('update_batch/', UpdateBatchView.as_view(), name='update_batch'),
    path('delete_batch/', DeleteBatchView.as_view(), name='delete_batch'),
    path('manage_semesters/', ManageSemestersView.as_view(), name='manage_semesters'),
    path('create_semester/', CreateSemesterView.as_view(), name='create_semester'),
    path('update_semester/', UpdateSemesterView.as_view(), name='update_semester'),
    path('delete_semester/', DeleteSemesterView.as_view(), name='delete_semester'),
    path('attendanceview/', AttendanceView.as_view(), name='attendanceview'),

    # Timetable Management
    path('timetable/', TimetableView.as_view(), name='timetable'),
    path('set_time_table/<str:day>/<str:period>/<str:classname>/', SetTimeTableView.as_view(), name='set_time_table'),
    path('update_time_table/<str:day>/<str:period>/<str:classname>/', UpdateTimeTableView.as_view(), name='update_time_table'),
    path('delete_time_table/', DeleteTimeTableView.as_view(), name='delete_time_table'),
    path('view_timetable/<str:classname>/', ViewTimeTableView.as_view(), name='view_time_table'),
    
    # Notice Management
    # Teacher Views (for full CRUD operations)
    path('student-notices/', StudentNoticeView.as_view(), name='student_notice'),
    path('create_student_notice/', CreateStudentNoticeView.as_view(), name='create_student_notice'),
    path('update_student_notice/', UpdateStudentNoticeView.as_view(), name='update_student_notice'),
    path('delete_student_notice/', DeleteStudentNoticeView.as_view(), name='delete_student_notice'),

    path('teacher-notices/', TeacherNoticeView.as_view(), name='teacher_notice'),
    path('create_teacher_notice/', CreateTeacherNoticeView.as_view(), name='create_teacher_notice'),
    path('update_teacher_notice/', UpdateTeacherNoticeView.as_view(), name='update_teacher_notice'),
    path('delete_teacher_notice/', DeleteTeacherNoticeView.as_view(), name='delete_teacher_notice'),
    
    # URL for adding or updating college details
    path('add-college-details/', CollegeDetailsView.as_view(), name='add_college_details'),# URL for adding a new subject
    path('add-subject/', AddSubjectView.as_view(), name='add_subject'),# URL for adding a new department course
    path('add-department-course/', AddDepartmentCourseView.as_view(), name='add_department_course'),# URL for deleting a subject or department course entry (ID-based)
    path('delete-entry/<int:entry_id>/', DeleteEntryView.as_view(), name='delete_entry'),
]

