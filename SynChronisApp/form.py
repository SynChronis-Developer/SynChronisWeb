from django import forms
from django.forms import ModelForm

from SynChronisApp.models import *


class LocationForm(ModelForm):
    class Meta:
        model = LocationTable
        fields = ['location_name', 'polygon_coordinates']
        
class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimeTableTable
        fields = ['SubjectName', 'TeacherName', 'ClassName', 'day', 'period', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

        
class ClassForm(ModelForm):
    class Meta:
        model = ClassTable
        fields = ['ClassName', 'TeacherName', 'Latitude', 'Longitude', 'Location_name', 'Semester']
        
class TeacherForm(ModelForm):
    class Meta:
        model = TeacherTable
        fields = ['TeacherName', 'Gender', 'SubjectName','Qualification','Email', 'Phone_number']
        
class SubjectsForm(ModelForm):
    class Meta:
        model = SubjectsTable
        fields = ['SubjectName','Semester','Year_of_Syllabus']
        
class NotesForm(ModelForm):
    class Meta:
        model = NotesTable
        fields = ['SubjectName', 'Teacher', 'Class_name', 'Unit', 'Notes']
        
class LoginForm(ModelForm):
    class Meta:
        model = LoginTable
        fields = ['Username', 'Password']
        
class StudentForm(ModelForm):
    class Meta:
        model = StudentTable
        fields = ['StudentName', 'Gender', 'Admission_no','Guardian_relation','Address','BatchYear','Semester','Age','Email', 'Phone_number','ClassName','Guardian_name','Guardian_phone','Date_of_birth','Blood_group']
        
class StudentNoticeForm(forms.ModelForm):
    class Meta:
        model = StudentNoticeTable
        fields = ['Notice_name', 'Notice_Content', 'File_Attachment']


    
class TeacherNotificationForm(ModelForm):
    class Meta:
        model = TeacherNoticeTable
        fields =[ 'NoticeContent', 'NoticeName',  'FileAttachment']

class LeaveApplicationForm(ModelForm):
    class Meta:
        model = LeaveApplicationTable
        fields = ['StudentName', 'Date', 'Reason', 'Status']
        


    # Add placeholders or initial labels for fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ClassName'].queryset = ClassTable.objects.all()

class CollegeDetailsForm(forms.ModelForm):
    class Meta:
        model = CollegeDetailsTable
        fields = ['name', 'email', 'phone_number', 'principal_name', 'principal_contact']
        
class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseTable
        fields = ['CourseName', 'Department', 'CourseDuration', 'CourseDescription', 'CourseCode']


class DepartmentForm(ModelForm):
    class Meta:
        model = DepartmentsTable
        fields = ['Department', 'department_id',]  # Assuming you have a related field for CollegeDetails


class SubjectForm(forms.ModelForm):
    class Meta:
        model = SubjectsTable
        fields = ['SubjectName', 'Semester', 'Year_of_Syllabus', 'Subject_code', 'Department']
