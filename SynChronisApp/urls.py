
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView
from .views import *
from SynChronisApp import views


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
    path('Add_Notice_Teacher/',TeacherNoticeView.as_view(), name='add_teacher_notice'),
    
    # URL pattern for adding student notice
    path('Add_Notice_Student/', StudentNoticeView.as_view(), name='add_student_notice'),
    
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
    

    # Timetable Management
    path('timetable/', TimetableView.as_view(), name='timetable'),
    path('timetable/set/', set_timetable, name='set_timetable'),
    path('timetable/delete/', DeleteTimetableView.as_view(), name='delete_timetable'),
    path('timetable/view/<str:classname>/', ViewTimetableView.as_view(), name='view_timetable'),
    
    # Notice Management
    # Student Notice Views (for full CRUD operations)
    path('create_update_student_notice/', StudentNoticeCreateUpdateView.as_view(), name='create_update_student_notice'),
    path('student-notices/<int:notice_id>/edit/', StudentNoticeDetailView.as_view(), name='edit_student_notice'),
    path('delete_student_notice/', StudentNoticeDeleteView.as_view(), name='delete_student_notice'),
    path('student-notices/', StudentNoticeListView.as_view(), name='list_student_notices'),
    
    #teacher notice
    path('teacher-notices/', TeacherNoticeListView.as_view(), name='teacher_notice_list'),
    path('teacher-notices/create/', TeacherNoticeCreateUpdateView.as_view(), name='create_teacher_notice'),
    path('teacher-notices/update/<int:notice_id>/', TeacherNoticeCreateUpdateView.as_view(), name='update_teacher_notice'),
    path('teacher-notices/detail/<int:notice_id>/', TeacherNoticeDetailView.as_view(), name='teacher_notice_detail'),
    path('teacher-notices/delete/', TeacherNoticeDeleteView.as_view(), name='delete_teacher_notice'),
    
    # Add college details
    path('college_details/', CollegeDetailsView.as_view(), name='college_details'),
    path('add_college_details/', CollegeDetailsCreateView.as_view(), name='add_college_details'),
    path('update_college_details/', CollegeDetailsUpdateView.as_view(), name='update_college_details'),
    path('delete_college_details/', CollegeDetailsDeleteView.as_view(), name='delete_college_details'),
    
    #department details
    path('departments/', DepartmentsView.as_view(), name='departments_list'),  # For listing departments
    path('manage_departments/', ManageDepartmentsView.as_view(), name='manage_departments'),
    path('add_department/', AddDepartmentView.as_view(), name='add_department'),
    path('update_department/<int:pk>/', UpdateDepartmentView.as_view(), name='update_department'),
    path('delete_department/<int:pk>/', DeleteDepartmentView.as_view(), name='delete_department'),
    
    #add course
    path('manage_courses/', ManageCoursesView.as_view(), name='manage_courses'),
    path('update_course/<int:pk>/', UpdateCourseView.as_view(), name='update_course'),
    path('delete_course/<int:pk>/', DeleteCourseView.as_view(), name='delete_course'),
    
    #add subject
    path('subjects_management/', ManageSubjectsView.as_view(), name='subjects_management'),
    path('subjects/manage/', ManageSubjectsView.as_view(), name='manage_subjects'),
    path('subjects/update/<int:pk>/', EditSubjectView.as_view(), name='edit_subject'),
    path('subjects/delete/<int:pk>/', DeleteSubjectView.as_view(), name='delete_subject'),
    
    #class and class teacher allocation
    
    path("class-teacher-list/", ClassTeacherListView.as_view(), name="class_teacher_list"),
    path("assign-teacher/", AssignTeacherView.as_view(), name="assign_teacher"),
    path("remove-teacher/", RemoveTeacherView.as_view(), name="remove_teacher"),
    path("class-teacher-allocation/", TemplateView.as_view(template_name="class_teacher_allocation.html"), name="class_teacher_allocation"),


    #class room locations
    path('add_class_location/', AddClassLocationView.as_view(), name='add_class_location'),
    path('view_class_locations/', ClassLocationListView.as_view(), name='view_class_locations'),
    path('update_class_location/<int:pk>/', UpdateClassLocationView.as_view(), name='update_class_location'),
    path('delete_class_location/<int:pk>/', DeleteClassLocationView.as_view(), name='delete_class_location'),
    path('save_class_location/', views.save_class_location, name='save_class_location'),
    
    # Attendance Dashboard View
    path('attendanceview/', views.AttendanceView.as_view(), name='attendanceview'),
    # Student Attendance Views
    path('attendance/student/<int:student_id>/monthly/<int:year>/<int:month>/', views.StudentMonthlyAttendanceView.as_view(), name='student_monthly_attendance'),
    path('attendance/student/<int:student_id>/semester/<int:semester_id>/', views.StudentSemesterAttendanceView.as_view(), name='student_semester_attendance'),
    # Class Attendance Views
    path('attendance/class/<int:class_id>/monthly/<int:year>/<int:month>/', views.ClassMonthlyAttendanceView.as_view(), name='class_monthly_attendance'),
    path('attendance/class/<int:class_id>/semester/<int:semester_id>/', views.ClassSemesterAttendanceView.as_view(), name='class_semester_attendance'),
    
    
    
    #mobile app
    path('api/android-login', AndroidLoginAPIView.as_view(), name='android_login_api'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    path('api/teacher/register/', InitiateTeacherRegistrationView.as_view(), name='teacher-register'),
    path('api/teacher/verify-otp/', VerifyRegistrationOTPView.as_view(), name="teacher-verify-otp"),
    
    # API to fetch a teacher's timetable
    path('api/view-teacher-timetable/<int:teacher_id>/', TeacherTimetableAPIView.as_view(), name='view-teacher-timetable'),
    # API to download a teacher's timetable as a PDF
     #attendance mark student
    path('fetch-timetable/<int:id>', FetchTimeTableView.as_view(), name='fetch-timetable'),
    path('mark-attendance/<int:id>', MarkAttendanceView.as_view(), name='mark-attendance'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)