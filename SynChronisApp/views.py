from django.contrib import messages
from django.core.paginator import Paginator
from datetime import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
import json
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from .form import BatchForm, LocationForm, StudentNoticeForm, TeacherNotificationForm, TimeTableForm
from .models import (
    BatchTable, ClassTable, CollegeDetailsTable, CourseTable, DepartmentsTable, LoginTable, SemesterTable, StudentNoticeTable, 
    StudentTable, SubjectsTable, TeacherNoticeTable, TeacherTable, TimeTableTable
)
import logging
from datetime import datetime

# Initialize logger for tracking events and errors
logger = logging.getLogger(__name__)
Date = datetime.now()

# Helper function to redirect with an alert message
def redirect_with_alert(url, message):
    # This function creates an alert popup and then redirects to the given URL
    return HttpResponse(f'''<script>alert('{message}');window.location.href='{url}';</script>''')

# View for rendering the login page and handling login logic
class LoginPage(View):
    def get(self, request):
        # Renders the login page for the user
        return render(request, 'adminlog.html')
    
    def post(self, request):
        # Handles the POST request when the user submits the login form
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            # Try to get a user with the given username and password
            obj = LoginTable.objects.get(Username=username, Password=password)
            if obj.Type == 'admin':
                # If the user is an Admin, show the admin dashboard
                return render(request, 'admindashboard.html')
            else:
                # If the user is not an Admin, show an invalid credentials alert
                return redirect_with_alert('/Login_page', 'Invalid Credentials')
        except LoginTable.DoesNotExist:
            # If no user is found, show an error message and reload the login page
            messages.error(request, 'Invalid username or password')
            return render(request, 'adminlog.html')

# Views for managing teacher approval and rejection
class ViewTeacher(View):
    def get(self, request):
        # Fetch all teachers from the TeacherTable and display them
        teachers = TeacherTable.objects.all()
        return render(request, 'viewteacher.html', {'teachers': teachers})

class AcceptTeacher(View):
    def get(self, request, id):
        # Accept a teacher by setting their status to 'Accept'
        teacher = TeacherTable.objects.get(id=id)
        teacher.LOGIN.status = 'Accept'
        teacher.LOGIN.save()
        return redirect('View_Teacher')

class RejectTeacher(View):
    def get(self, request, id):
        # Reject a teacher by setting their status to 'Reject'
        teacher = TeacherTable.objects.get(id=id)
        teacher.LOGIN.status = 'Reject'
        teacher.LOGIN.save()
        return redirect('View_Teacher')

# Timetable Views to handle timetable-related functionality
class TimetableView(View):
    def get(self, request):
        # Fetch all classes, subjects, and teachers to display in the timetable creation page
        classes = ClassTable.objects.all()
        subjects = SubjectsTable.objects.all()
        teachers = TeacherTable.objects.all()
        return render(request, 'timetable.html', {'classes': classes, 'subjects': subjects, 'teachers': teachers})

class SetTimeTableView(View):
    def post(self, request, day, period, classname):
        # Set the timetable for a particular day and period based on the class name, subject, and teacher
        subject_id = request.POST.get(f'subject-{day}-{period}')
        teacher_id = request.POST.get(f'teacher-{day}-{period}')
        start_time = request.POST.get(f'StartTime-{day}-{period}')
        end_time = request.POST.get(f'EndTime-{day}-{period}')

        # Check if all required fields are provided
        if not subject_id or not teacher_id or not start_time or not end_time:
            return HttpResponseBadRequest("Missing required fields.")

        try:
            # Fetch class, subject, and teacher instances based on IDs
            class_instance = ClassTable.objects.get(ClassName=classname)
            subject_instance = SubjectsTable.objects.get(id=subject_id)
            teacher_instance = TeacherTable.objects.get(id=teacher_id)
        except (ClassTable.DoesNotExist, SubjectsTable.DoesNotExist, TeacherTable.DoesNotExist):
            return JsonResponse({'message': 'Invalid class, subject, or teacher.'}, status=404)

        # Create or update the timetable entry for the given class, day, and period
        timetable, created = TimeTableTable.objects.update_or_create(
            Day=day, Period=period, ClassName=class_instance,
            defaults={'SubjectName': subject_instance, 'StartTime': start_time, 'EndTime': end_time, 'TeacherName': teacher_instance}
        )
        # Return a success message indicating whether a new timetable entry was created
        return JsonResponse({'message': 'Timetable updated successfully.', 'created': created})

class UpdateTimeTableView(View):
    def post(self, request, day, period, classname):
        # Update the timetable for a specific day and period
        subject_name = request.POST.get('SubjectName')
        start_time = request.POST.get('StartTime')
        end_time = request.POST.get('EndTime')

        # Check if any required fields are missing
        if not subject_name or not start_time or not end_time:
            return HttpResponseBadRequest("Missing required fields.")

        try:
            # Fetch the class, subject, and teacher instances
            class_instance = ClassTable.objects.get(ClassName=classname)
            subject_instance = SubjectsTable.objects.get(SubjectName=subject_name)
        except (ClassTable.DoesNotExist, SubjectsTable.DoesNotExist):
            return JsonResponse({'message': 'Invalid class or subject.'}, status=404)

        # Update the timetable for the given day and period
        timetable = TimeTableTable.objects.filter(ClassName=class_instance, Day=day, Period=period).first()
        if timetable:
            timetable.SubjectName = subject_instance
            timetable.StartTime = start_time
            timetable.EndTime = end_time
            timetable.save()
            return JsonResponse({'message': 'Timetable updated successfully.'})
        else:
            return JsonResponse({'message': 'No timetable entry found for this period.'}, status=404)


# Delete the timetable entry for a specific class, day, and period
class DeleteTimeTableView(View):
    def post(self, request):
        classname = request.POST.get('classname')
        day = request.POST.get('day')
        period = request.POST.get('period')

        if not classname or not day or not period:
            return HttpResponseBadRequest("Missing required fields.")

        try:
            class_instance = ClassTable.objects.get(ClassName=classname)
            timetable = TimeTableTable.objects.get(Day=day, Period=period, ClassName=class_instance)
            timetable.delete()
        except (ClassTable.DoesNotExist, TimeTableTable.DoesNotExist):
            return JsonResponse({'message': 'Timetable entry not found.'}, status=404)

        return JsonResponse({'success': True, 'message': 'Timetable deleted successfully.'})

# View to retrieve the timetable for a given class and return it in JSON format
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

class ViewTimeTableView(View):
    def get(self, request, classname):
        """
        Return the timetable for the specified class in JSON format.
        """
        class_instance = get_object_or_404(ClassTable, ClassName=classname)
        timetable = TimeTableTable.objects.filter(ClassName=class_instance)

        # Prepare the data for the response
        timetable_data = {day: {} for day in weekdays}
        for entry in timetable:
            timetable_data[entry.Day][entry.Period] = {
                'subjectName': entry.SubjectName.SubjectName,
                'teacherName': entry.TeacherName.TeacherName
            }

        return JsonResponse(timetable_data)
class MainPage(View):
    def get(self, request):
        return render(request, 'mainpage.html')

class AdminDashboard(View):
    def get(self, request):
        return render(request, 'admindashboard.html')
    
class Location(View):
    def get(self, request):
        return render(request, 'location.html')
    def post(self, request):
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('''<script>alert('location added successfully');window.location.href='/Location';</script>''')
       
class SelectTime_Table(View):
    def get(self, request):
        return render(request, 'selecttimetable.html')
    
    
class SendLeaveApplication(View):
    def get(self, request):
        return render(request, 'leaveapplication.html')
        
class Addnotes(View):
    def get(self, request):
        return render(request, 'addnotes.html')
    
class ViewNotes(View):
    def get(self, request):
        return render(request, 'viewnotes.html')
    

class ApproveLeaveApplication(View):
    def get(self, request):
        return render(request, 'viewleaveapplication.html')
    
class AdminNotificationControl(View):
    def get(self, request):
        return render(request, 'adminnotificationcontrol.html')
    
class AddTeacherNoticeView(View):
    def get(self, request):
        # Render the form for adding a teacher notice
        return render(request, 'teacher_notice_page.html')  # Replace with actual template

    def post(self, request):
        # Handle form submission and add teacher notice
        # Example: Create a new notice from the form data
        TeacherNoticeTable.objects.create(
            
            NoticeName=request.POST['NoticeName'],
            NoticeContent=request.POST['NoticeContent'],
            FileAttachment=request.FILES.get('FileAttachment'),
        )
        return redirect('adminnotificationcontrol')  # Redirect to the notifications page
class AddStudentNoticeView(View):
    def get(self, request):
        # Get all batches from the database
        batches = BatchTable.objects.all()
        return render(request, 'student_notice_page.html', {'batches': batches})
    def view_student_notices(request):
    # Fetch all student notices
        studentnotices = StudentNoticeTable.objects.all()
    
        return render(request, 'student_notice_page.html', {'studentnotices': studentnotices})

    def post(self, request):
        # Handle form submission for student notice
        batch_ids = request.POST.getlist('BatchName')  # Get selected batch IDs
        notice_name = request.POST['Notice_name']
        notice_content = request.POST['Notice_Content']
        file_attachment = request.FILES.get('File_Attachment')

        # Create a new notice and associate it with selected batches
        notice = StudentNoticeTable.objects.create(
            Notice_name=notice_name,
            Notice_Content=notice_content,
            File_Attachment=file_attachment
        )
        
        # Associate the notice with the selected batches
        for batch_id in batch_ids:
            batch = BatchTable.objects.get(id=batch_id)
            notice.BatchName.add(batch)  # Add batch to the ManyToMany field

        notice.save()

        return redirect('adminnotificationcontrol')  # Redirect to the notifications page

    

class BatchView(View):
    def get(self, request):
        classes = ClassTable.objects.all()
        # Fetch all batches from the database
        batches = BatchTable.objects.all()
        return render(request, 'batch_page.html', {'batches': batches, 'classes': classes})

# Create Batch View
class CreateBatchView(View):
    def post(self, request):
        # Extract data from POST request
        batch_name = request.POST.get('BatchName')
        batch_year = request.POST.get('BatchYear')
        batch_start_year = request.POST.get('BatchStartYear')
        batch_end_year = request.POST.get('BatchEndYear')

        # Create a new batch
        batch = BatchTable.objects.create(
            BatchName=batch_name,
            BatchYear=batch_year,
            BatchStartYear=batch_start_year,
            BatchEndYear=batch_end_year
        )

        return JsonResponse({
            'success': True,
            'batch_id': batch.id,
            'batch_name': batch.BatchName,
            'batch_year': batch.BatchYear,
            'batch_start_year': batch.BatchStartYear,
            'batch_end_year': batch.BatchEndYear
        })

# Update Batch View
class UpdateBatchView(View):
    def post(self, request):
        # Extract data from POST request
        batch_id = request.POST.get('batchId')
        batch_name = request.POST.get('BatchName')
        batch_year = request.POST.get('BatchYear')
        batch_start_year = request.POST.get('BatchStartYear')
        batch_end_year = request.POST.get('BatchEndYear')

        # Update the batch
        batch = BatchTable.objects.get(id=batch_id)
        batch.BatchName = batch_name
        batch.BatchYear = batch_year
        batch.BatchStartYear = batch_start_year
        batch.BatchEndYear = batch_end_year
        batch.save()

        return JsonResponse({
            'success': True,
            'batch_id': batch.id,
            'batch_name': batch.BatchName,
            'batch_year': batch.BatchYear,
            'batch_start_year': batch.BatchStartYear,
            'batch_end_year': batch.BatchEndYear
        })

# Delete Batch View
class DeleteBatchView(View):
    def post(self, request):
        # Extract batch ID from POST request
        batch_id = request.POST.get('batchId')

        # Delete the batch
        batch = BatchTable.objects.get(id=batch_id)
        batch.delete()

        return JsonResponse({'success': True})

# Render the Semester Management Page

class ManageSemestersView(View):
    def get(self, request):
        batches = BatchTable.objects.all()
        semesters = SemesterTable.objects.all()
        return render(request, 'managesemester.html', {'batches': batches, 'semesters': semesters})

class CreateSemesterView(View):
    def post(self, request):
        try:
            batch = get_object_or_404(BatchTable, id=request.POST.get('BatchName'))
            semester = SemesterTable.objects.create(
                BatchName=batch,
                Semester=request.POST.get('Semester'),
                StartDate=request.POST.get('StartDate'),
                EndDate=request.POST.get('EndDate'),
            )
            return JsonResponse({
                'success': True,
                'semester_id': semester.id,
                'batch_name': semester.BatchName.BatchName,
                'semester': semester.Semester,
                'start_date': semester.StartDate,
                'end_date': semester.EndDate,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

class UpdateSemesterView(View):
    def post(self, request):
        try:
            semester = get_object_or_404(SemesterTable, id=request.POST.get('semesterId'))
            semester.BatchName = get_object_or_404(BatchTable, id=request.POST.get('BatchName'))
            semester.Semester = request.POST.get('Semester')
            semester.StartDate = request.POST.get('StartDate')
            semester.EndDate = request.POST.get('EndDate')
            semester.save()

            return JsonResponse({
                'success': True,
                'batch_name': semester.BatchName.BatchName,
                'semester': semester.Semester,
                'start_date': semester.StartDate,
                'end_date': semester.EndDate,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

class DeleteSemesterView(View):
    def post(self, request):
        try:
            semester = get_object_or_404(SemesterTable, id=request.POST.get('semesterId'))
            semester.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})


class AttendanceView(View):
    def get(self, request):
        return render(request, 'attendanceview.html')
    

# Assuming you have a form class for this


# View to fetch batches
# View to list all notices
# Teacher Views (for CRUD operations)

# Student Notices View
class StudentNoticeView(View):
    def get(self, request):
        student_notices = StudentNoticeTable.objects.all()
        batches = BatchTable.objects.all()
        return render(request, 'student_notice_page.html', {'student_notices': student_notices, 'batches': batches})


# Create Student Notice
class CreateStudentNoticeView(View):
    def post(self, request):
        notice_name = request.POST.get('NoticeName')
        notice_content = request.POST.get('NoticeContent')
        file_attachment = request.FILES.get('FileAttachment')
        batch_ids = request.POST.getlist('BatchName')

        notice = StudentNoticeTable.objects.create(
            Notice_name=notice_name,
            Notice_Content=notice_content,
            File_Attachment=file_attachment,
            
            
        )

        for batch_id in batch_ids:
            batch = BatchTable.objects.get(id=batch_id)
            notice.BatchName.add(batch)

        return JsonResponse({
            'success': True,
            'notice_id': notice.id,
            'notice_name': notice.Notice_name,
            'notice_content': notice.Notice_Content,
            'file_attachment_url': notice.File_Attachment.url if notice.File_Attachment else None
        })

# Update Student Notice


class UpdateStudentNoticeView(View):
    def post(self, request):
        notice_id = request.POST.get('noticeId')
        notice_name = request.POST.get('NoticeName')
        notice_content = request.POST.get('NoticeContent')
        file_attachment = request.FILES.get('FileAttachment')
        batch_ids = request.POST.getlist('BatchName')

        notice = get_object_or_404(StudentNoticeTable, id=notice_id)
        notice.Notice_name = notice_name
        notice.Notice_Content = notice_content
        if file_attachment:
            notice.File_Attachment = file_attachment
        notice.save()

        notice.BatchName.clear()
        for batch_id in batch_ids:
            batch = BatchTable.objects.get(id=batch_id)
            notice.BatchName.add(batch)

        return JsonResponse({
            'success': True,
            'notice_id': notice.id,
            'notice_name': notice.Notice_name,
            'notice_content': notice.Notice_Content,
            'file_attachment_url': notice.File_Attachment.url if notice.File_Attachment else None
        })

# Delete Student Notice
class DeleteStudentNoticeView(View):
    def post(self, request):
        notice_id = request.POST.get('noticeId')
        notice = get_object_or_404(StudentNoticeTable, id=notice_id)
        notice.delete()

        return JsonResponse({'success': True})


# Teacher Notices View
class TeacherNoticeView(View):
    def get(self, request):
        teacher_notices = TeacherNoticeTable.objects.all()
        departments = ClassTable.objects.all()
        return render(request, 'teacher_notice_page.html', {'teacher_notices': teacher_notices, 'departments': departments})

# Create Teacher Notice
class CreateTeacherNoticeView(View):
    def post(self, request):
        notice_name = request.POST.get('NoticeName')
        notice_content = request.POST.get('NoticeContent')
        file_attachment = request.FILES.get('FileAttachment')
        department_id = request.POST.get('Department')

        department = ClassTable.objects.get(id=department_id)

        notice = TeacherNoticeTable.objects.create(
            NoticeName=notice_name,
            NoticeContent=notice_content,
            FileAttachment=file_attachment,
            Department=department
        )

        return JsonResponse({
            'success': True,
            'notice_id': notice.id,
            'notice_name': notice.NoticeName,
            'notice_content': notice.NoticeContent,
            'file_attachment_url': notice.FileAttachment.url if notice.FileAttachment else None
        })

# Update Teacher Notice
class UpdateTeacherNoticeView(View):
    def post(self, request):
        notice_id = request.POST.get('noticeId')
        notice_name = request.POST.get('NoticeName')
        notice_content = request.POST.get('NoticeContent')
        file_attachment = request.FILES.get('FileAttachment')
        department_id = request.POST.get('Department')

        department = ClassTable.objects.get(id=department_id)

        notice = TeacherNoticeTable.objects.get(id=notice_id)
        notice.NoticeName = notice_name
        notice.NoticeContent = notice_content
        if file_attachment:
            notice.FileAttachment = file_attachment
        notice.Department = department
        notice.save()

        return JsonResponse({
            'success': True,
            'notice_id': notice.id,
            'notice_name': notice.NoticeName,
            'notice_content': notice.NoticeContent,
            'file_attachment_url': notice.FileAttachment.url if notice.FileAttachment else None
        })

# Delete Teacher Notice
class DeleteTeacherNoticeView(View):
    def post(self, request):
        notice_id = request.POST.get('noticeId')
        notice = TeacherNoticeTable.objects.get(id=notice_id)
        notice.delete()

        return JsonResponse({'success': True})
    
    
    
#college details view
class CollegeDetailsView(View):
    def get(self, request):
        # Fetch departments, courses, and semesters to populate the form
        departments = DepartmentsTable.objects.all()
        courses = CourseTable.objects.all()
        semesters = SemesterTable.objects.all()

        context = {
            'departments': departments,
            'courses': courses,
            'semesters': semesters
        }
        return render(request, 'addcollegedetails.html', context)

    def post(self, request):
        # Get or create the College Details instance
        college_details = CollegeDetailsTable.objects.first()  # Assuming only one record exists, or create a new one
        if not college_details:
            college_details = CollegeDetailsTable()
        
        # Capture form data
        college_details.name = request.POST.get('name')
        college_details.email = request.POST.get('email')
        college_details.phone_number = request.POST.get('phone_number')
        college_details.principal_name = request.POST.get('principal_name')
        college_details.principal_contact = request.POST.get('principal_contact')

        # Save or update the college details
        college_details.save()

        return JsonResponse({'status': 'success', 'message': 'College details saved successfully!'})

class AddSubjectView(View):
    def post(self, request):
        data = json.loads(request.body)
        
        # Get the necessary IDs
        department_id = data.get('department_id')
        course_id = data.get('course_id')
        semester_id = data.get('semester_id')
        subject_name = data.get('subject_name')

        # Validate the inputs
        if department_id and course_id and semester_id and subject_name:
            # Fetch the related objects
            department = DepartmentsTable.objects.filter(id=department_id).first()
            course = CourseTable.objects.filter(id=course_id).first()
            semester = SemesterTable.objects.filter(id=semester_id).first()

            if department and course and semester:
                # Create the new subject
                subject = SubjectsTable.objects.create(
                    SubjectName=subject_name,
                    Department=department,
                    Course=course,
                    Semester=semester
                )
                return JsonResponse({
                    'success': True, 
                    'subject_id': subject.id,
                    'message': 'Subject added successfully!'
                })

        return JsonResponse({'success': False, 'message': 'Invalid data provided!'}, status=400)

class AddDepartmentCourseView(View):
    def post(self, request):
        data = json.loads(request.body)
        department_name = data.get('department_name')
        course_name = data.get('course_name')
        if department_name and course_name:
            department_course = DepartmentsTable.objects.create(
                department_name=department_name,
                course_name=course_name
            )
            return JsonResponse({'success': True, 'department_id': department_course.id})
        return JsonResponse({'success': False}, status=400)

class DeleteEntryView(View):
    def post(self, request, entry_id):
        try:
            # Attempt to delete a Subject first
            subject = SubjectsTable.objects.filter(id=entry_id).first()
            if subject:
                subject.delete()
                return JsonResponse({'success': True})

            # If no Subject is found, attempt to delete a DepartmentCourse
            department_course = DepartmentsTable.objects.filter(id=entry_id).first()
            if department_course:
                department_course.delete()
                return JsonResponse({'success': True})

            return JsonResponse({'success': False}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        
