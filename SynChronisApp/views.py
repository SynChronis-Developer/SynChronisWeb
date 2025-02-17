import json
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.timezone import now
from .models import PasswordResetOTP, RegistrationOTP
import random
from rest_framework import generics

from django.utils.timezone import localtime
# Mark Attendance APIfrom datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated

from .models import AttendanceTable, ClassTable, TimeTableTable
from .serializers import AttendanceSerializer


from datetime import timedelta, datetime
from django.contrib.auth.hashers import check_password
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .serializers import TeacherSerializer, TimeTableSerializer
from .serializers import LoginSerializer
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import authenticate
from django.http import Http404, JsonResponse
from django.contrib.auth import login, logout
from django.shortcuts import  get_object_or_404
from .models import  SubjectsTable
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.forms import model_to_dict
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.http import  HttpResponse, HttpResponseBadRequest
from django.views import View
from django.views.generic import ListView
from .form import  *
from .models import *
import logging
from rest_framework.decorators import api_view

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
        department = DepartmentsTable.objects.all()
        sub = SubjectsTable.objects.all()
        te = TeacherTable.objects.all()
        return render(request, 'viewteacher.html', {'te': te , 'sub': sub, 'department': department})

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

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Timetable Page View
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']  # Updated weekdays

# Timetable Page View
class TimetableView(ListView):
    """
    Displays the timetable page with all classes, subjects, and teachers.
    """
    model = TimeTableTable
    template_name = 'timetable.html'
    context_object_name = 'timetable_entries'

    def get_queryset(self):
        return TimeTableTable.objects.select_related('ClassName', 'SubjectName', 'TeacherName')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = ClassTable.objects.all()
        context['subjects'] = SubjectsTable.objects.all()
        context['teachers'] = TeacherTable.objects.all()
        context['weekdays'] = weekdays
        context['form'] = TimetableEntryForm()
        return context


@csrf_exempt  # For handling AJAX POST requests
def set_timetable(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            classname_id = data.get('classname')
            periods = data.get('periods')
            timetable_entries = data.get('timetable', [])
            print(data,classname_id,periods)

            # Fetch class object
            class_obj = get_object_or_404(ClassTable, id=classname_id)

            # Clear existing timetable for this class (if needed)
            TimeTableTable.objects.filter(ClassName=class_obj).delete()
            def parse_time(time_str):
                    if time_str in [None, "", " "]:  # Handle empty values properly
                        return None
                    try:
                        return datetime.strptime(time_str, '%H:%M').time()
                    except ValueError:
                        return None 
            # Iterate over received timetable data and save
            for entry in timetable_entries:
                day = entry.get('day')
                period = entry.get('period')
                subject_id = entry.get('subject')
                teacher_id = entry.get('teacher')
                start_time = parse_time(entry.get('start_time'))
                end_time = parse_time(entry.get('end_time'))
                print(start_time,end_time)
                            # Function to convert time strings or empty values to None
 

                # Fetch subject and teacher objects
                subject_obj = SubjectsTable.objects.get(id=subject_id) if subject_id else None
                teacher_obj = TeacherTable.objects.get(id=teacher_id) if teacher_id else None

                # Create a new timetable entry
                c=TimeTableTable.objects.create(
                    ClassName=class_obj,
                    SubjectName=subject_obj,
                    TeacherName=teacher_obj,
                    day=day,
                    period=period,
                    start_time=start_time,
                    end_time=end_time
                )
                print(c)

            return JsonResponse({'success': True, 'message': 'Timetable saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# Set or Update Timetable Entry
class SetOrUpdateTimetableView(View):
    """
    Handles setting or updating a timetable entry for a class, day, and period.
    """
    def post(self, request, *args, **kwargs):
        data = request.POST
        classname = data.get('classname')
        day = data.get('day')
        period = data.get('period')
        subject_id = data.get('subject')
        teacher_id = data.get('teacher')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not classname or not day or not period or not subject_id:
            return JsonResponse({'message': 'Missing required fields.'}, status=400)

        class_instance = get_object_or_404(ClassTable, ClassName=classname)
        subject_instance = get_object_or_404(SubjectsTable, id=subject_id)
        teacher_instance = get_object_or_404(TeacherTable, id=teacher_id) if teacher_id else None

        timetable, created = TimeTableTable.objects.update_or_create(
            ClassName=class_instance, day=day, period=period,
            defaults={
                'SubjectName': subject_instance,
                'TeacherName': teacher_instance,
                'start_time': start_time,
                'end_time': end_time
            }
        )

        return JsonResponse({'message': 'Timetable updated successfully.', 'created': created})


# Delete Timetable Entry
class DeleteTimetableView(View):
    """
    Deletes a timetable entry based on class, day, and period.
    """
    def post(self, request, *args, **kwargs):
        classname = request.POST.get('classname')
        day = request.POST.get('day')
        period = request.POST.get('period')

        if not classname or not day or not period:
            return HttpResponseBadRequest("Missing required fields.")

        class_instance = get_object_or_404(ClassTable, ClassName=classname)
        timetable = TimeTableTable.objects.filter(ClassName=class_instance, day=day, period=period).first()

        if timetable:
            timetable.delete()
            return JsonResponse({'success': True, 'message': 'Timetable deleted successfully.'})
        return JsonResponse({'message': 'Timetable entry not found.'}, status=404)


# View Timetable
class ViewTimetableView(View):
    """
    Fetches and returns the timetable for a given class in JSON format.
    """
    def get(self, request, classname):
        class_instance = get_object_or_404(ClassTable, ClassName=classname)
        timetable = TimeTableTable.objects.filter(ClassName=class_instance).select_related('SubjectName', 'TeacherName')

        timetable_data = {day: {} for day in weekdays}
        for entry in timetable:
            timetable_data[entry.day][entry.period] = {
                'subjectName': entry.SubjectName.SubjectName,
                'teacherName': entry.TeacherName.TeacherName if entry.TeacherName else "N/A",
                'startTime': entry.start_time,
                'endTime': entry.end_time
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
        location_name = request.POST.get('location_name')
        polygon_coordinates = request.POST.get('polygon_coordinates')

        if not location_name or not polygon_coordinates:
            return HttpResponse(
                '''<script>alert('Please enter a location name and select a geofence area.');window.location.href='/Location';</script>'''
            )

        try:
            polygon_data = json.loads(polygon_coordinates)
        except json.JSONDecodeError:
            return HttpResponse(
                '''<script>alert('Invalid geofence coordinates format.');window.location.href='/Location';</script>'''
            )

        location_entry = LocationTable.objects.create(
            location_name=location_name,
            polygon_coordinates=polygon_data
        )
        location_entry.save()

        return HttpResponse(
            '''<script>alert('Geofence location added successfully!');window.location.href='/Location';</script>'''
        )
       
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
        teacher_notices = TeacherNoticeTable.objects.all()
        student_notices = StudentNoticeTable.objects.all()
        return render(request, 'adminnotificationcontrol.html', {'teacher_notices': teacher_notices, 'student_notices': student_notices})
    

class BatchView(View):
    def get(self, request):
        classes = ClassTable.objects.all()
        # Fetch all batches from the database
        return render(request, 'batch_page.html', {'classes': classes})

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
        semesters = SemesterTable.objects.all()
        return render(request, 'managesemester.html', { 'semesters': semesters})

class CreateSemesterView(View):
    def post(self, request):
        try:
            semester = SemesterTable.objects.create(
                Semester=request.POST.get('Semester'),
                StartDate=request.POST.get('StartDate'),
                EndDate=request.POST.get('EndDate'),
            )
            return JsonResponse({
                'success': True,
                'semester_id': semester.id,
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


# Attendance Dashboard View
class AttendanceView(View):
    def get(self, request):
        semesters = SemesterTable.objects.all()
        students = StudentTable.objects.all()
        classes = ClassTable.objects.all()
        attendance = AttendanceTable.objects.all()

        # Optional pagination for attendance records
        page = request.GET.get('page', 1)
        paginator = Paginator(attendance, 10)  # Adjust number per page as needed
        paged_attendance = paginator.get_page(page)

        return render(request, 'attendanceview.html', {
            'attendance': paged_attendance,
            'students': students,
            'classes': classes,
            'semesters': semesters
        })

# Student Monthly Attendance View
class StudentMonthlyAttendanceView(View):
    def get(self, request, student_id, year, month):
        try:
            # Validate the month and year
            if not (1 <= int(month) <= 12):
                return JsonResponse({'error': 'Invalid month'}, status=400)
            if len(str(year)) != 4:
                return JsonResponse({'error': 'Invalid year'}, status=400)
            
            start_date = datetime(year=int(year), month=int(month), day=1)
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(year=int(year), month=int(month) + 1, day=1)

            # Efficient querying with prefetch_related for related data (if needed)
            attendance_records = AttendanceTable.objects.filter(
                StudentName_id=student_id,
                Date__range=[start_date, end_date]
            ).select_related('StudentName')

            weekly_data = []
            week_data = {'week': 1, 'total_hours': 0, 'attended_hours': 0}
            for record in attendance_records:
                week_num = record.Date.isocalendar()[1]
                if week_num != week_data['week']:
                    weekly_data.append(week_data)
                    week_data = {'week': week_num, 'total_hours': 0, 'attended_hours': 0}

                week_data['total_hours'] += record.TotalHours
                week_data['attended_hours'] += record.AttendedHours
            weekly_data.append(week_data)

            return render(request, 'attendance/student_monthly_attendance.html', {
                'weekly_data': weekly_data,
                'student_id': student_id,
                'year': year,
                'month': month
            })

        except AttendanceTable.DoesNotExist:
            raise Http404("No attendance records found.")

# Student Semester Attendance View
class StudentSemesterAttendanceView(View):
    def get(self, request, student_id, semester_id):
        try:
            semester = SemesterTable.objects.get(id=semester_id)
            semester_months = self.get_semester_months(semester)

            attendance_records = AttendanceTable.objects.filter(
                StudentName_id=student_id,
                Date__month__in=semester_months
            )

            semester_data = []
            total_hours = 0
            attended_hours = 0
            for record in attendance_records:
                semester_data.append({
                    'Month': record.Date.strftime('%B'),
                    'TotalHours': record.TotalHours,
                    'AttendedHours': record.AttendedHours,
                    'Attendance': record.Attendance
                })
                total_hours += record.TotalHours
                attended_hours += record.AttendedHours

            attendance_percentage = (attended_hours / total_hours) * 100 if total_hours else 0

            return render(request, 'attendance/student_semester_attendance.html', {
                'semester_data': semester_data,
                'attendance_percentage': attendance_percentage,
                'student_id': student_id,
                'semester_id': semester_id
            })

        except AttendanceTable.DoesNotExist:
            raise Http404("No attendance records found.")

    def get_semester_months(self, semester):
        start_date = semester.StartDate
        end_date = semester.EndDate
        semester_months = []

        current_date = start_date
        while current_date <= end_date:
            semester_months.append(current_date.month)
            current_date = current_date.replace(month=current_date.month % 12 + 1)
            if current_date.month == 1:
                current_date = current_date.replace(year=current_date.year + 1)

        return semester_months

# Class Monthly Attendance View
class ClassMonthlyAttendanceView(View):
    def get(self, request, class_id):
        month = request.GET.get('month')
        year = request.GET.get('year')

        if not month or not year:
            return JsonResponse({'error': 'Month and Year are required'}, status=400)

        try:
            students_in_class = StudentTable.objects.filter(ClassName=class_id)

            attendance_data = AttendanceTable.objects.filter(
                StudentName__ClassName=class_id,
                Date__month=month,
                Date__year=year
            )

            student_attendance = {}
            for student in students_in_class:
                student_name = student.StudentName
                student_attendance[student_name] = {
                    'total_days': 0,
                    'days_present': 0,
                    'attendance': []
                }

                student_attendance_data = attendance_data.filter(StudentName=student)

                for attendance in student_attendance_data:
                    student_attendance[student_name]['attendance'].append({
                        'date': attendance.Date,
                        'status': attendance.Status,
                        'attendance': attendance.Attendance
                    })

                    if attendance.Status.lower() == 'present':
                        student_attendance[student_name]['days_present'] += 1
                    student_attendance[student_name]['total_days'] += 1

            return JsonResponse(student_attendance)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# Class Semester Attendance View
class ClassSemesterAttendanceView(View):
    def get(self, request, class_id, semester_id):
        try:
            semester = SemesterTable.objects.get(id=semester_id)
            semester_months = self.get_semester_months(semester)

            students = StudentTable.objects.filter(ClassName_id=class_id)
            class_data = []

            for student in students:
                attendance_records = AttendanceTable.objects.filter(
                    StudentName_id=student.id,
                    Date__month__in=semester_months
                )

                total_hours = sum([record.TotalHours for record in attendance_records])
                attended_hours = sum([record.AttendedHours for record in attendance_records])

                attendance_percentage = (attended_hours / total_hours) * 100 if total_hours else 0

                class_data.append({
                    'student': student,
                    'total_hours': total_hours,
                    'attended_hours': attended_hours,
                    'attendance_percentage': attendance_percentage
                })

            return render(request, 'attendance/class_semester_attendance.html', {
                'class_data': class_data,
                'semester_id': semester_id,
                'class_id': class_id
            })

        except AttendanceTable.DoesNotExist:
            raise Http404("No attendance records found.")

    def get_semester_months(self, semester):
        start_date = semester.StartDate
        end_date = semester.EndDate
        semester_months = []

        current_date = start_date
        while current_date <= end_date:
            semester_months.append(current_date.month)
            current_date = current_date.replace(month=current_date.month % 12 + 1)
            if current_date.month == 1:
                current_date = current_date.replace(year=current_date.year + 1)

        return semester_months
    
class CollegeDetailsView(View):
    def get(self, request, *args, **kwargs):
        # Query based on the logged-in user
        teachers = TeacherTable.objects.all()
        classes = ClassTable.objects.all()
        subjects = SubjectsTable.objects.all()
        courses = CourseTable.objects.all()
        dments = DepartmentsTable.objects.all()
        college_details = CollegeDetailsTable.objects.filter(user=request.user).first()
        form = CollegeDetailsForm(instance=college_details)
        
        return render(request, 'addcollegedetails.html', 
                        {'form': form, 
                        'college_details': college_details , 
                        'dments': dments , 
                        'courses': courses , 
                        'subjects': subjects
                        , 'classes': classes,
                        'teachers': teachers,}
                        )

    def post(self, request, *args, **kwargs):
        # Handle form submission (add or update)
        college_details = CollegeDetailsTable.objects.filter(user=request.user).first()
        if college_details:
            form = CollegeDetailsForm(request.POST, instance=college_details)
        else:
            form = CollegeDetailsForm(request.POST)
        
        if form.is_valid():
            form.save()
            return render(request, 'addcollegedetails.html', {'form': form, 'college_details': form.instance})
        return render(request, 'addcollegedetails.html', {'form': form})
    
    
    
    
class CollegeDetailsCreateView(View):
    def post(self, request):
        form = CollegeDetailsForm(request.POST)
        if form.is_valid():
            college_details = form.save(commit=False)
            college_details.Login = request.user  # Associate with the logged-in user
            college_details.save()

            return JsonResponse({
                'success': True,
                'message': 'College details added successfully!',
                'action': 'add',
                'college': {
                    'name': college_details.name,
                    'email': college_details.email,
                    'phone_number': college_details.phone_number,
                    'principal_name': college_details.principal_name,
                    'principal_contact': college_details.principal_contact,
                }
            })
        return JsonResponse({'success': False, 'message': 'Form submission failed!'}, status=400)
    
class CollegeDetailsUpdateView(View):
    def post(self, request):
        try:
            # Get the existing college details for the logged-in user
            college_details = CollegeDetailsTable.objects.get(user=request.user)
            
            # Bind the form to the existing instance
            form = CollegeDetailsForm(request.POST, instance=college_details)
            
            if form.is_valid():
                form.save()  # Save the updated college details
                return JsonResponse({
                    'success': True,
                    'message': 'College details updated successfully!',
                    'action': 'update',
                    'college': {
                        'name': college_details.name,
                        'email': college_details.email,
                        'phone_number': college_details.phone_number,
                        'principal_name': college_details.principal_name,
                        'principal_contact': college_details.principal_contact,
                    }
                })
            return JsonResponse({'success': False, 'message': 'Form submission failed!'}, status=400)
        
        except CollegeDetailsTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No college details found for this user.'})

class CollegeDetailsDeleteView(View):
    def post(self, request):
        try:
            college_details = CollegeDetailsTable.objects.get(user=request.user)  # Use 'user' instead of 'Login'
            college_details.delete()
            return JsonResponse({'success': True, 'message': 'College details deleted successfully!'})
        except CollegeDetailsTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No college details found for this user.'})
        
        
# View for listing and rendering the departments page

# Common validation function for department ID and name
def validate_department_input(department_id, department_name):
    if not department_id or not department_id.isdigit():
        return False, 'Department ID must be a valid number.'
    
    if not department_name or department_name.strip() == '':
        return False, 'Department name cannot be empty.'
    
    return True, None

class DepartmentsView(View):
    def get(self, request):
        # Fetch all department records
        dments = DepartmentsTable.objects.all()
        context = {
            'dments': dments,  # Pass the data to the template
        }
        return render(request, 'addcollegedetails.html', context)
    
# Custom View for viewing and adding departments
class ManageDepartmentsView(View):
    def get(self, request):
        # Fetch all departments
        departments = DepartmentsTable.objects.all()

        # Create the form for adding a new department
        form = DepartmentForm()

        # Pass the departments and form to the template
        return render(request, 'manage_departments.html', {
            'departments': departments,
            'form': form
        })

    def post(self, request):
        # Handle form submission for adding a new department
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new department to the database
            return self.get(request)  # Reload the page with the updated list of departments

        # If form is not valid, render the page with the form errors
        departments = DepartmentsTable.objects.all()
        return render(request, 'manage_departments.html', {
            'departments': departments,
            'form': form
        })
        
        
class AddDepartmentView(View):
    def post(self, request):
        data = request.POST
        department_id = data.get('department_id')
        department_name = data.get('Department')

        # Validate inputs
        is_valid, error_message = validate_department_input(department_id, department_name)
        if not is_valid:
            return JsonResponse({'success': False, 'message': error_message})

        department_id = int(department_id)  # Convert to integer
        
        # Check if the department already exists
        if DepartmentsTable.objects.filter(department_id=department_id).exists():
            return JsonResponse({'success': False, 'message': 'Department ID already exists.'})

        # Create new department
        department = DepartmentsTable.objects.create(
            department_id=department_id,
            Department=department_name.strip()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Department added successfully',
            'department': {
                'id': department.id,
                'department_id': department.department_id,
                'Department': department.Department
            }
        })
@method_decorator(csrf_exempt, name='dispatch')
class UpdateDepartmentView(View):
    def post(self, request, pk):
        department_id = request.POST.get('department_id')
        department_name = request.POST.get('Department')

        is_valid, error_message = validate_department_input(department_id, department_name)
        if not is_valid:
            return JsonResponse({'success': False, 'message': error_message})

        try:
            department = DepartmentsTable.objects.get(id=pk)
            department.department_id = department_id
            department.Department = department_name.strip()
            department.save()

            return JsonResponse({
                'success': True,
                'message': 'Department updated successfully',
                'department': {
                    'id': department.id,
                    'department_id': department.department_id,
                    'Department': department.Department
                }
            })
        except DepartmentsTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Department not found'})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteDepartmentView(View):
    def post(self, request, pk):
        try:
            department = DepartmentsTable.objects.get(id=pk)
            department_name = department.Department
            department.delete()
            return JsonResponse({'success': True, 'message': f'Department "{department_name}" deleted successfully'})
        except DepartmentsTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Department not found'})
        
class ManageCoursesView(View):
    def get(self, request):
        courses = CourseTable.objects.all()
        departments = DepartmentsTable.objects.all()
        form = CourseForm()

        return render(request, 'manage_courses.html', {
            'courses': courses,
            'departments': departments,
            'form': form
        })

    def post(self, request):
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Course added successfully'})
        return JsonResponse({'success': False, 'message': 'Error adding course'})

class UpdateCourseView(View):
    def post(self, request, pk):
        course = CourseTable.objects.get(id=pk)
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Course updated successfully'})
        return JsonResponse({'success': False, 'message': 'Error updating course'})

class DeleteCourseView(View):
    def post(self, request, pk):
        try:
            course = CourseTable.objects.get(id=pk)
            course.delete()
            return JsonResponse({'success': True, 'message': 'Course deleted successfully'})
        except CourseTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Course not found'})
        
        
class SubjectManagementView(View):
    def get(self, request):
        return render(request, 'managesubjects.html')   
        
# Subject Management View
class ManageSubjectsView(View):
    def get(self, request):
        departments = DepartmentsTable.objects.all()
        courses = CourseTable.objects.all()
        semesters = SemesterTable.objects.all()
        subjects = SubjectsTable.objects.all()

        return render(request, 'managesubjects.html', {
            'departments': departments,
            'courses': courses,
            'semesters': semesters,
            'subjects': subjects
        })
    
    def post(self, request):
        subject_code = request.POST.get('subject_code')
        subject_name = request.POST.get('subject_name')
        department_id = request.POST.get('department_id')
        course_id = request.POST.get('course_id')
        year_of_syllabus = request.POST.get('year_of_syllabus')
        semester_id = request.POST.get('semester')
        
        # Check if the subject already exists (if needed)
        try:
            department = DepartmentsTable.objects.get(id=department_id)
            course = CourseTable.objects.get(id=course_id)
            semester = SemesterTable.objects.get(id=semester_id)

            # Create the subject
            subject = SubjectsTable.objects.create(
                Subject_code=subject_code,
                SubjectName=subject_name,
                Department=department,
                Course=course,
                Year_of_Syllabus=year_of_syllabus,
                Semester=semester
            )

            # Respond with a success message
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Subject created successfully!'})
            return redirect('manage_subjects')
        except (DepartmentsTable.DoesNotExist, CourseTable.DoesNotExist, SemesterTable.DoesNotExist):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid data provided.'})
            return redirect('manage_subjects')

# Edit Subject View
# Edit Subject View
class EditSubjectView(View):
    def get(self, request, pk):
        try:
            subject = SubjectsTable.objects.get(id=pk)
            departments = DepartmentsTable.objects.all()
            courses = CourseTable.objects.all()
            semesters = SemesterTable.objects.all()

            return JsonResponse({
                'success': True,
                'subject': {
                    'id': subject.id,
                    'Subject_code': subject.Subject_code,
                    'SubjectName': subject.SubjectName,
                    'Department': subject.Department.id,
                    'Course': subject.Course.id,
                    'Year_of_Syllabus': subject.Year_of_Syllabus,
                    'Semester': subject.Semester.id
                },
                'departments': [{'id': d.id, 'name': d.Department} for d in departments],
                'courses': [{'id': c.id, 'name': c.CourseName} for c in courses],
                'semesters': [{'id': s.id, 'name': s.Semester} for s in semesters]
            })
        except SubjectsTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Subject not found.'})

    def post(self, request, pk):
        try:
            subject = SubjectsTable.objects.get(id=pk)
            subject_code = request.POST.get('subject_code')
            subject_name = request.POST.get('subject_name')
            department_id = request.POST.get('department_id')
            course_id = request.POST.get('course_id')
            year_of_syllabus = request.POST.get('year_of_syllabus')
            semester_id = request.POST.get('semester')

            department = DepartmentsTable.objects.get(id=department_id)
            course = CourseTable.objects.get(id=course_id)
            semester = SemesterTable.objects.get(id=semester_id)

            # Update subject
            subject.Subject_code = subject_code
            subject.SubjectName = subject_name
            subject.Department = department
            subject.Course = course
            subject.Year_of_Syllabus = year_of_syllabus
            subject.Semester = semester
            subject.save()

            # Respond with a success message
            return JsonResponse({'success': True, 'message': 'Subject updated successfully!'})
        except (DepartmentsTable.DoesNotExist, CourseTable.DoesNotExist, SemesterTable.DoesNotExist, SubjectsTable.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid data provided.'})


# Delete Subject View
class DeleteSubjectView(View):
    def post(self, request, pk):
        try:
            subject = SubjectsTable.objects.get(id=pk)

            # Delete subject
            subject.delete()

            # Respond with a success message
            return JsonResponse({'success': True, 'message': 'Subject deleted successfully!'})
        except SubjectsTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Subject not found.'})
        
        
        
        
# class and class teacher allocation
class ClassTeacherListView(View):
    """Fetch and display all class-teacher allocations."""

    def get(self, request):
        classes = ClassTable.objects.all().select_related('TeacherName')
        teachers = TeacherTable.objects.all()
        
        data = {
            "classes": [
                {
                    "id": cls.id,
                    "class_name": cls.ClassName,
                    "teacher": cls.TeacherName.TeacherName if cls.TeacherName else "Not Assigned",
                    "teacher_id": cls.TeacherName.id if cls.TeacherName else None
                }
                for cls in classes
            ],
            "teachers": [
                {
                    "id": teacher.id,
                    "name": teacher.TeacherName
                }
                for teacher in teachers
            ]
        }
        return JsonResponse(data)


class AssignTeacherView(View):
    """Assign or update a teacher for a class."""

    def post(self, request):
        class_id = request.POST.get("class_id")
        teacher_id = request.POST.get("teacher_id")

        if not class_id or not teacher_id:
            return JsonResponse({"success": False, "message": "Missing class or teacher ID."}, status=400)

        class_obj = get_object_or_404(ClassTable, id=class_id)
        teacher_obj = get_object_or_404(TeacherTable, id=teacher_id)

        # Check if the teacher is already assigned to another class
        if ClassTable.objects.filter(TeacherName=teacher_obj).exclude(id=class_id).exists():
            return JsonResponse({"success": False, "message": f"Teacher {teacher_obj.TeacherName} is already assigned to another class."}, status=400)

        class_obj.TeacherName = teacher_obj
        class_obj.save()

        return JsonResponse({"success": True, "message": f"Teacher {teacher_obj.TeacherName} assigned to {class_obj.ClassName}"})



class RemoveTeacherView(View):
    """Remove a teacher from a class (unassign teacher)."""

    def delete(self, request):
        try:
            # Ensure request body is not empty
            if not request.body:
                return JsonResponse({"success": False, "message": "Empty request body."}, status=400)

            # Load JSON data
            data = json.loads(request.body)  
            class_id = data.get("class_id")

            if not class_id:
                return JsonResponse({"success": False, "message": "Missing class ID."}, status=400)

            # Fetch the class object
            class_obj = get_object_or_404(ClassTable, id=class_id)
            
            if not class_obj.TeacherName:
                return JsonResponse({"success": False, "message": "No teacher assigned to this class."}, status=400)

            # Unassign teacher
            class_obj.TeacherName = None  
            class_obj.save()

            return JsonResponse({"success": True, "message": f"Teacher removed from {class_obj.ClassName}"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON format."}, status=400)

        
        
# Add Class Location View
class AddClassLocationView(View):
    def get(self, request):
        context = {
            'semesters': SemesterTable.objects.all(),
            'departments': DepartmentsTable.objects.all(),
            'teachers': TeacherTable.objects.all(),
            'classesl': ClassTable.objects.all(),
        }
        return render(request, 'add_class_location.html', context)

    # In your AddClassLocationView or UpdateClassLocationView:

# In your AddClassLocationView or UpdateClassLocationView:

def post(self, request):
    # Extract data from the form
    class_name = request.POST.get("class_name")
    latitude = request.POST.get("latitude")
    longitude = request.POST.get("longitude")
    location_name = request.POST.get("location_name")
    year = request.POST.get("year")
    radius = request.POST.get("radius")  # Ensure you're capturing radius correctly
    semester_id = request.POST.get("semester")
    department_id = request.POST.get("department")
    teacher_id = request.POST.get("teacher")

    try:
        # Fetch related objects
        semester = SemesterTable.objects.get(id=semester_id)
        department = DepartmentsTable.objects.get(id=department_id)
        teacher = TeacherTable.objects.get(id=teacher_id)

        # Create the ClassTable instance with the correct field names
        ClassTable.objects.create(
            ClassName=class_name,  # Correct field name
            Latitude=latitude,  # Correct field name
            Longitude=longitude,  # Correct field name
            Location_name=location_name,  # Correct field name
            Radius=radius,  # Correct field name
            Year=year,
            Semester=semester,
            Department=department,
            TeacherName=teacher,
        )

        return redirect('view_class_locations')  # Redirect after success

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})



# List View of Class Locations
class ClassLocationListView(View):
    def get(self, request):
        locations = ClassTable.objects.all()
        context = {
            'locations': locations,
            'semesters': SemesterTable.objects.all(),
            'departments': DepartmentsTable.objects.all(),
            'teachers': TeacherTable.objects.all(),
        }
        return render(request, 'view_class_locations.html', context)


# Update Class Location View
class UpdateClassLocationView(View):
    def get(self, request, pk):
        location = get_object_or_404(ClassTable, pk=pk)
        context = {
            'location': location,
            'semesters': SemesterTable.objects.all(),
            'departments': DepartmentsTable.objects.all(),
            'teachers': TeacherTable.objects.all(),
        }
        return render(request, 'update_class_location.html', context)

    def post(self, request, pk):
        location = get_object_or_404(ClassTable, pk=pk)

        class_name = request.POST.get("class_name")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        location_name = request.POST.get("location_name")
        year = request.POST.get("year")
        semester_id = request.POST.get("semester")
        department_id = request.POST.get("department")
        teacher_id = request.POST.get("teacher")

        try:
            semester = SemesterTable.objects.get(id=semester_id)
            department = DepartmentsTable.objects.get(id=department_id)
            teacher = TeacherTable.objects.get(id=teacher_id)

            # Update the location
            location.ClassName = class_name
            location.Latitude = latitude
            location.Longitude = longitude
            location.Location_name = location_name
            location.Year = year
            location.Semester = semester
            location.Department = department
            location.TeacherName = teacher
            location.save()

            # Return a success response with updated data
            return JsonResponse({
                "success": True,
                "message": "Class location updated successfully!",
                "location": {
                    "class_name": location.ClassName,
                    "location_name": location.Location_name,
                    "year": location.Year,
                    "latitude": location.Latitude,
                    "longitude": location.Longitude,
                    "semester": location.Semester.name,
                    "department": location.Department.name,
                    "teacher": location.TeacherName.name,
                }
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


# Delete Class Location View
class DeleteClassLocationView(View):
    def post(self, request, pk):
        location = get_object_or_404(ClassTable, pk=pk)

        try:
            location.delete()  # Delete the location
            return JsonResponse({
                "success": True,
                "message": "Class location deleted successfully!"
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
        
        
def save_class_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        radius = request.POST.get('radius')  # Get radius as string
        class_name = request.POST.get('class_name')
        location_name = request.POST.get('location_name')

        try:
            # Ensure radius is an integer
            radius = int(radius)  # Cast radius to integer

            # Create the ClassTable instance with the correct field names
            ClassTable.objects.create(
                ClassName=class_name,  # Correct field name
                Latitude=latitude,  # Correct field name
                Longitude=longitude,  # Correct field name
                Location_name=location_name,  # Correct field name
                Radius=radius,  # Correct field name
            )
            return JsonResponse({"success": True, "message": "Class location added successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


#for student notices
class StudentNoticeView(View):
    def get(self, request):
        notices = StudentNoticeTable.objects.all()
        return render(request, 'student_notice_page.html', {'notices': notices})


@method_decorator(csrf_exempt, name='dispatch')
class StudentNoticeCreateUpdateView(View):
    def post(self, request, *args, **kwargs):
        try:
            notice_id = request.POST.get('noticeId')
            notice_name = request.POST.get('NoticeName')
            notice_content = request.POST.get('NoticeContent')
            notice_type = request.POST.get('NoticeType')  # Notice Type from form
            file_attachment = request.FILES.get('FileAttachment')

            if notice_id:
                # Update an existing notice
                notice = get_object_or_404(StudentNoticeTable, id=notice_id)
                notice.Notice_name = notice_name
                notice.Notice_Content = notice_content
                notice.Notice_Type = notice_type
                if file_attachment:
                    notice.File_Attachment = file_attachment
                notice.save()

         
                return JsonResponse({'success': True, 'message': 'Notice updated successfully!'})
            else:
                # Create a new notice
                notice = StudentNoticeTable.objects.create(
                    Notice_name=notice_name,
                    Notice_Content=notice_content,
                    Notice_Type=notice_type,
                    File_Attachment=file_attachment,
                )

         

                return JsonResponse({'success': True, 'message': 'Notice created successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class StudentNoticeDetailView(View):
    def get(self, request, *args, **kwargs):
        try:
            notice_id = kwargs.get('notice_id')
            notice = get_object_or_404(StudentNoticeTable, id=notice_id)
            notice_data = model_to_dict(notice)

            # Convert File_Attachment to a URL string (if it exists)
            if notice.File_Attachment:
                notice_data['File_Attachment'] = notice.File_Attachment.url
            else:
                notice_data['File_Attachment'] = None

            notice_data['BatchName'] = list(notice.BatchName.values('id', 'BatchName'))
            notice_data['Notice_Type'] = notice.Notice_Type

            return JsonResponse({'success': True, 'data': notice_data})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class StudentNoticeDeleteView(View):
    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            notice_id = body.get('noticeId')
            notice = get_object_or_404(StudentNoticeTable, id=notice_id)
            notice.delete()
            return JsonResponse({'success': True, 'message': 'Notice deleted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class StudentNoticeListView(View):
    def get(self, request, *args, **kwargs):
        try:
            notices = StudentNoticeTable.objects.all()
            data = []
            for notice in notices:
                data.append({
                    'id': notice.id,
                    'Notice_name': notice.Notice_name,
                    'Notice_Content': notice.Notice_Content,
                    'Notice_Type': notice.Notice_Type,
                    'File_Attachment': notice.File_Attachment.url if notice.File_Attachment else None,
                    'BatchName': list(notice.BatchName.values('id', 'BatchName')),
                    'Date': localtime(notice.Date).strftime('%Y-%m-%d %H:%M:%S'),
                })

            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        

# Teacher Notice Views
class TeacherNoticeView(View):
    def get(self, request, *args, **kwargs):
        departments = DepartmentsTable.objects.all()
        teacher_notices = TeacherNoticeTable.objects.all()
        return render(request, 'teacher_notice_page.html', {'teacher_notices': teacher_notices, 'departments': departments})


@method_decorator(csrf_exempt, name='dispatch')
class TeacherNoticeCreateUpdateView(View):
    def post(self, request, *args, **kwargs):
        try:
            notice_id = request.POST.get('noticeId')
            notice_name = request.POST.get('NoticeName')
            notice_content = request.POST.get('NoticeContent')
            department_ids = request.POST.getlist('Department')  # Department IDs
            file_attachment = request.FILES.get('FileAttachment')

            if not notice_name or not notice_content:
                return JsonResponse({'success': False, 'message': 'Notice name and content are required.'})

            # Check if it's an update or creation
            if notice_id:
                # Update existing notice
                notice = get_object_or_404(TeacherNoticeTable, id=notice_id)
                notice.NoticeName = notice_name
                notice.NoticeContent = notice_content

                # Handle file attachment
                if file_attachment:
                    if file_attachment.content_type in ['application/pdf', 'image/jpeg', 'image/png']:
                        notice.FileAttachment = file_attachment
                    else:
                        return JsonResponse({'success': False, 'message': 'Invalid file type. Only PDF, JPEG, or PNG are allowed.'})

                notice.save()
                if department_ids:
                    notice.Department.set(DepartmentsTable.objects.filter(id__in=department_ids))
                
                # Return the updated notice
                file_url = notice.FileAttachment.url if notice.FileAttachment else None
                return JsonResponse({'success': True, 'message': 'Notice updated successfully!', 'data': self.prepare_notice_data(notice, file_url)})

            else:
                # Create new notice
                notice = TeacherNoticeTable.objects.create(
                    NoticeName=notice_name,
                    NoticeContent=notice_content,
                    FileAttachment=file_attachment,
                )
                if department_ids:
                    notice.Department.set(DepartmentsTable.objects.filter(id__in=department_ids))
                
                file_url = notice.FileAttachment.url if notice.FileAttachment else None
                return JsonResponse({'success': True, 'message': 'Notice created successfully!', 'data': self.prepare_notice_data(notice, file_url)})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})

    def prepare_notice_data(self, notice, file_url):
        # Prepare the notice data to be returned
        return {
            'id': notice.id,
            'NoticeName': notice.NoticeName,
            'NoticeContent': notice.NoticeContent,
            'Date': notice.Date.strftime('%Y-%m-%d %H:%M:%S'),
            'FileAttachment': file_url,
            'Department': list(notice.Department.values('id', 'Department')),
        }


class TeacherNoticeListView(View):
    def get(self, request, *args, **kwargs):
        try:
            teacher_notices = TeacherNoticeTable.objects.all()
            data = [
                {
                    'id': notice.id,
                    'NoticeName': notice.NoticeName,
                    'NoticeContent': notice.NoticeContent,
                    'Date': notice.Date.strftime('%Y-%m-%d %H:%M:%S'),
                    'FileAttachment': notice.FileAttachment.url if notice.FileAttachment else None,
                    'Department': [{'id': dept.id, 'Department': dept.Department} for dept in notice.Department.all()]
                }
                for notice in teacher_notices
            ]
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})


class TeacherNoticeDetailView(View):
    def get(self, request, *args, **kwargs):
        try:
            notice_id = kwargs.get('notice_id')
            notice = get_object_or_404(TeacherNoticeTable, id=notice_id)
            notice_data = model_to_dict(notice)
            notice_data['Department'] = list(notice.Department.values('id', 'Department'))
            notice_data['FileAttachment'] = notice.FileAttachment.url if notice.FileAttachment else None
            return JsonResponse({'success': True, 'data': notice_data})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})


@method_decorator(csrf_exempt, name='dispatch')
class TeacherNoticeDeleteView(View):
    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            notice_id = body.get('noticeId')
            notice = get_object_or_404(TeacherNoticeTable, id=notice_id)
            notice.delete()
            return JsonResponse({'success': True, 'message': 'Notice deleted successfully!'})
        except TeacherNoticeTable.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Notice not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})
        
        
        
        
        
########################################################################
########################################################################
#                                                                      #
##                          Android APIs                              ##
#                                                                      #
########################################################################
########################################################################



class AndroidLoginAPIView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)  # Allow JSON & Form data

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = LoginTable.objects.get(Username=username, Type__in=["student", "teacher"])
            
            # Directly compare the plain text passwords
            if password != user.Password:  
                return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        except LoginTable.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "message": "success",
            "user_id": user.id,
            "username": user.Username,
            "user_type": user.Type
        }, status=status.HTTP_200_OK)



class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            user = LoginTable.objects.get(Email=email)  # Fix here
        except LoginTable.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Remove any previous OTPs
        PasswordResetOTP.objects.filter(Username=user).delete()

        # Store OTP in database
        PasswordResetOTP.objects.create(Username=user, otp=otp)

        # Send OTP email
        send_mail(
            "Password Reset OTP",
            f"""
<html>
  <body style="font-family: 'Helvetica Neue', sans-serif; background-color: #f4f4f4; color: #333; margin: 0; padding: 0; text-align: center;">
    <div style="width: 100%; max-width: 650px; margin: 0 auto; padding: 40px 20px; background-color: #ffffff; border-radius: 15px; box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1); text-align: left;">
      
      <h2 style="color: #2C3E50; font-size: 30px; margin-bottom: 20px; font-family: 'Georgia', serif;">Password Reset Request</h2>
      
      <p style="font-size: 18px;">Dear <strong>{user.Username}</strong>,</p>
      <p style="font-size: 16px;">We have received a request to reset your password for the <strong>Synchronis app</strong>. Please find your One-Time Password (OTP) below:</p>
      
      <!-- OTP Box with inline styles -->
      <div style="text-align: center; margin-top: 0px; padding: 25px 25px; background-color: #2ecc71; color: white; font-size: 36px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); font-weight: bold; display: inline-block;">
        <strong>{otp}</strong>
      </div>
      
      <p style="font-size: 16px;">This OTP is valid for the next <strong>5 minutes</strong>. Kindly use it to reset your password. If you did not request a password reset, please ignore this message.</p>
      
      <div style="background-color: #ecf0f1; padding: 15px; margin-top: 20px; border-radius: 8px; font-size: 16px;">
        <strong>To:</strong><br>
        <strong>Name:</strong> {user.Username}<br>
        <strong>Email:</strong> {user.Email}
      </div>

      <p style="font-size: 16px; margin-top: 20px;">Thank you,<br><span style="font-size: 18px; font-weight: bold; color: #2C3E50; margin-top: 20px;">SynChronis Support Team</span></p>
      
      <p style="font-size: 16px; color: #777; margin-top: 40px;">Contact us: <a href="mailto:synchronis.developer@gmail.com" style="color: #3498db; text-decoration: none; font-weight: bold;">synchronis.developer@gmail.com</a></p>
    </div>
  </body>
</html>
""",
            "synchronis.developer@gmail.com",  # Update this with your sender email
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        try:
            user = LoginTable.objects.get(Email=email)  # Fix here
            reset_otp = PasswordResetOTP.objects.get(Username=user, otp=otp)
        except (LoginTable.DoesNotExist, PasswordResetOTP.DoesNotExist):
            return Response({"error": "Invalid OTP or Email"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP is expired
        if reset_otp.is_expired():
            reset_otp.delete()
            return Response({"error": "OTP expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        # Update user password
        user.Password = new_password
        user.save()

        # Mark OTP as used and delete it
        reset_otp.is_used = True
        reset_otp.save()
        reset_otp.delete()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
    
 # Import your models

# 1️⃣ Initiate Teacher Registration (Generate OTP)
class InitiateTeacherRegistrationView(APIView):  # Kept original view name
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not name or not email or not password:
            return Response({"error": "All fields are required!"}, status=status.HTTP_400_BAD_REQUEST)

        if LoginTable.objects.filter(Email=email).exists():
            return Response({"error": "Email already registered!"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        # Store OTP in database
        otp_entry, created = RegistrationOTP.objects.update_or_create(
            Email=email,
            defaults={"otp": otp_code, "is_used": False, "created_at": now()}
        )

        # Send OTP via email
        try:
            email_message = EmailMessage(
                subject="Your Registration OTP",
                body=f"Hello {name},\nYour OTP for registration is: {otp_code}\nThis OTP is valid for 2 minutes.",
                from_email="synchronis.developer@gmail.com",
                to=[email]
            )
            email_message.send()
        except Exception as e:
            return Response({"error": f"Failed to send OTP. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent successfully! Please verify your email."}, status=status.HTTP_200_OK)


# 2️⃣ Verify OTP and Register the User
class VerifyRegistrationOTPView(APIView):  # Kept original view name
    def post(self, request):
        print("Received Data:", request.data)  # Debugging line

        email = request.data.get("email")
        otp = request.data.get("otp")
        name = request.data.get("name")
        password = request.data.get("password")

        if not email or not otp or not name or not password:
            return Response({"error": "All fields are required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_entry = RegistrationOTP.objects.filter(Email=email, otp=otp, is_used=False).latest("created_at")

            # ✅ Check if OTP expired (valid for 2 minutes)
            if (now() - otp_entry.created_at).total_seconds() > 120:
                return Response({"error": "OTP expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used
            otp_entry.is_used = True
            otp_entry.save()

            # ✅ Create user in LoginTable AFTER OTP verification
            LoginTable.objects.create(
                Username=name,
                Email=email,
                Password=password,  # Plaintext password as you requested
                Type="teacher",
                status="active"
            )

            return Response({"message": "Account verified and registered successfully! You can now log in."}, status=status.HTTP_201_CREATED)

        except RegistrationOTP.DoesNotExist:
            return Response({"error": "Invalid OTP or Email"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Something went wrong. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        



class TeacherTimetableAPIView(APIView):
    """
    API to fetch a specific teacher's timetable.
    """

    def get(self, request, teacher_id):
        teacher_instance = get_object_or_404(TeacherTable, id=teacher_id)
        timetable_entries = TimeTableTable.objects.filter(TeacherName=teacher_instance).select_related('ClassName', 'SubjectName')

        if not timetable_entries.exists():
            return Response({'message': 'No timetable found for this teacher.'}, status=status.HTTP_404_NOT_FOUND)

        timetable_data = []
        for entry in timetable_entries:
            timetable_data.append({
                'class_name': entry.ClassName.ClassName,
                'day': entry.day,
                'period': entry.period,
                'subject_name': entry.SubjectName.SubjectName,
                'start_time': entry.start_time.strftime('%H:%M') if entry.start_time else None,
                'end_time': entry.end_time.strftime('%H:%M') if entry.end_time else None
            })

        return Response({'timetable': timetable_data}, status=status.HTTP_200_OK)




class DownloadTeacherTimetablePDFAPI(APIView):
    """
    API to generate and download a teacher's timetable as a PDF (Using ReportLab).
    """

    def get(self, request, teacher_id):
        teacher_instance = get_object_or_404(TeacherTable, id=teacher_id)
        timetable_entries = TimeTableTable.objects.filter(TeacherName=teacher_instance).select_related('ClassName', 'SubjectName')

        if not timetable_entries.exists():
            return Response({'message': 'No timetable found for this teacher.'}, status=status.HTTP_404_NOT_FOUND)

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{teacher_instance.TeacherName}_timetable.pdf"'

        # Create a PDF canvas
        pdf = canvas.Canvas(response, pagesize=letter)
        pdf.setTitle(f"{teacher_instance.TeacherName} Timetable")

        # PDF Header
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 750, f"Timetable for {teacher_instance.TeacherName}")

        # Table Header
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, 710, "Class")
        pdf.drawString(150, 710, "Day")
        pdf.drawString(250, 710, "Period")
        pdf.drawString(350, 710, "Subject")
        pdf.drawString(450, 710, "Time")

        # Draw a line below header
        pdf.line(50, 705, 550, 705)

        # Add timetable entries
        y_position = 690
        pdf.setFont("Helvetica", 11)
        for entry in timetable_entries:
            pdf.drawString(50, y_position, entry.ClassName.ClassName)
            pdf.drawString(150, y_position, entry.day)
            pdf.drawString(250, y_position, str(entry.period))
            pdf.drawString(350, y_position, entry.SubjectName.SubjectName)
            start_time = entry.start_time.strftime('%H:%M') if entry.start_time else 'N/A'
            end_time = entry.end_time.strftime('%H:%M') if entry.end_time else 'N/A'
            pdf.drawString(450, y_position, f"{start_time} - {end_time}")

            y_position -= 20  # Move to the next line

            # Create a new page if needed
            if y_position < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y_position = 750

        pdf.save()  # Save the PDF
        return response  # Return the generated PDF



from math import radians, sin, cos, sqrt, atan2

# Function to calculate distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    # Ensure all inputs are floats
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])

    R = 6371000  # Radius of Earth in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c 

# Fetch Timetable API
from django.utils.timezone import localtime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import TimeTableTable
from .serializers import TimeTableSerializer


class FetchTimeTableView(APIView):
  

    def get(self, request,id, *args, **kwargs):
        student=StudentTable.objects.filter(LOGIN__id=id).first()
        print(student.ClassName.id)
        
        class_id = ClassTable.objects.filter(id=student.ClassName.id).first()
        print(class_id)
        if not class_id:
            return Response({"message": "class_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # day = localtime().strftime("%A") 
        # print(day)# Get today's day
        day='Monday'
        timetable_entries = TimeTableTable.objects.filter(ClassName__id=class_id.id, day=day)

        if not timetable_entries.exists():
            return Response({"message": "No timetable available for today."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TimeTableSerializer(timetable_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from datetime import datetime, timedelta
from django.utils.timezone import localtime

class MarkAttendanceView(APIView):
    def post(self, request,id, *args, **kwargs):
        # class_id = request.data.get("class_id")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        student=StudentTable.objects.filter(LOGIN__id=id).first()
        class_id = ClassTable.objects.filter(id=student.ClassName.id).first()
        print('------------->', request.data)

        if not class_id or latitude is None or longitude is None:
            print('---------if---->')
            return Response({"message": "Missing required fields."}, status=status.HTTP_200_OK)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            print(latitude,longitude)
        except ValueError:
            print('---------expt---->')

            return Response({"message": "Invalid latitude or longitude values."}, status=status.HTTP_200_OK)
        from datetime import datetime, date,time
        # current_time = localtime().time()
        # Set Default Date and Time
        DEFAULT_DATE = date(2025, 2, 17)  # ✅ Example default date
        DEFAULT_TIME = datetime.strptime("18:45:00", "%H:%M:%S").time()  # ✅ Example default time

        # Use defaults instead of system time
        today = DEFAULT_DATE  # ✅ Ensure today is a `date` object
        current_time = DEFAULT_TIME  # ✅ Ensure current_time is a `time` object
        weekday_name = today.strftime("%A")  # ✅ Convert date to weekday name

        print("Current Time:", current_time, "Today:", today, "Weekday:", weekday_name)

        # Query periods that have started today
        periods = TimeTableTable.objects.filter(
            day=weekday_name,  # ✅ Ensure it matches database format ("Monday", "Tuesday", etc.)
            start_time__lte=current_time  # ✅ Get periods that have already started
        )

        print("Periods:", periods)

        # Manually filter for periods where current_time is within 20 minutes after start_time
        current_period = None
        for period in periods:
            start_time = period.start_time
            print("start_time",start_time)
            start_plus_20 = (datetime.combine(today, start_time) + timedelta(minutes=40)).time()  # ✅ Fixed TypeError

            if start_time <= current_time <= start_plus_20:
                current_period = period
                break  # ✅ Stop when we find the valid period
        
        print("Current Period:", current_period)
        if not current_period:
            print('---------cur period---->')

            return Response({"message": "No active period for attendance."}, status=status.HTTP_200_OK)

        # Get class Geo-fence location
      
        
        class_instance = ClassTable.objects.filter(id=class_id.id).first()
        print("class_instance",class_instance)
  
        class_lat, class_lon, radius = class_instance.Latitude, class_instance.Longitude, class_instance.Radius

        # Check if user is within allowed geofence radius
        distance = haversine(class_lat, class_lon, latitude, longitude)
        print(distance)
        if distance > radius:
            print('---------cur period---->')
            return Response({"error": "You are outside the allowed geofence area."}, status=status.HTTP_200_OK)

        # Mark Attendance
        attendance, created = AttendanceTable.objects.get_or_create(
            StudentName=student,
            Period=current_period,
            Date=today,
            defaults={"Status": "Present", "Attendance": 1},
        )

        if not created:
            return Response({"message": "Attendance already marked."}, status=status.HTTP_200_OK)

        return Response({"message": "Attendance marked successfully."}, status=status.HTTP_201_CREATED)
