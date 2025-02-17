from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import random



# User login table
class LoginTable(models.Model):
    UType = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('class_teacher', 'Class Teacher'),
    ]
    
    Username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    Password = models.CharField(max_length=128, null=True, blank=True)
    Email = models.EmailField(unique=True, null=True, blank=True) 
    Type = models.CharField(max_length=50, choices=UType, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)



class PasswordResetOTP(models.Model):
    Username = models.ForeignKey(LoginTable, on_delete=models.CASCADE,null=True, blank=True)
    otp = models.CharField(max_length=6)  # 6-digit OTP
    created_at = models.DateTimeField(auto_now_add=True)  # OTP created time
    is_used = models.BooleanField(default=False)  # Track if OTP is used

    def is_expired(self):
        """ Check if OTP is expired (valid for 5 minutes) """
        return (now() - self.created_at).total_seconds() > 300  # 5 minutes (300 sec)


class RegistrationOTP(models.Model):
    Email = models.EmailField(unique=True, null=True, blank=True)  # Store email temporarily
    otp = models.CharField(max_length=6)  # 6-digit OTP
    created_at = models.DateTimeField(auto_now_add=True)  # OTP timestamp
    is_used = models.BooleanField(default=False)  # Track if OTP is used

    def is_expired(self):
        return (now() - self.created_at).total_seconds() > 120  # Expires in 2 minutes

    def __str__(self):
        return f"{self.Email} - OTP: {self.otp} - Used: {self.is_used}"

# Department details table
class DepartmentsTable(models.Model):
    department_id = models.IntegerField(null=False, blank=False)
    Department = models.CharField(max_length=50, null=True, blank=True)
#department details table

# Course details table
class CourseTable(models.Model):
    CourseName = models.CharField(max_length=50, null=True, blank=True)
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    CourseDuration = models.CharField(max_length=50, null=True, blank=True)
    CourseDescription = models.CharField(max_length=500, null=True, blank=True)
    CourseCode = models.CharField(max_length=50, null=True, blank=True)

# Semester details table
class SemesterTable(models.Model):
    Semester = models.CharField(max_length=50, null=True, blank=True)
    StartDate = models.DateField(null=True, blank=True)
    EndDate = models.DateField(null=True, blank=True)
    course = models.ForeignKey(CourseTable, on_delete=models.CASCADE, null=True, blank=True)


# Subject details table
class SubjectsTable(models.Model): 
    SType=[
        ('Class Room', 'Class Room'),
        ('Computer Lab', 'Computer Lab'),
        ('Electronics Lab', 'Electronics Lab'),
        ('Physics Lab', 'Physics Lab'),
        ('Chemistry Lab', 'Chemistry Lab'),
        ('Biology Lab', 'Biology Lab'),
        ('Maths Lab', 'Maths Lab'),
        ('Library', 'Library'),
        ('Auditorium', 'Auditorium'),
        ('Seminar Hall', 'Seminar Hall'),
    ]
    Subject_code = models.CharField(max_length=50, null=True, blank=True)
    SubjectName = models.CharField(max_length=50, null=True, blank=True)
    SubjectType = models.CharField(max_length=50, choices=SType, null=True, blank=True)
    Department = models.ForeignKey('DepartmentsTable', on_delete=models.CASCADE, null=True, blank=True)
    Year_of_Syllabus = models.CharField(max_length=50, null=True, blank=True)
    Semester = models.ForeignKey(SemesterTable, on_delete=models.CASCADE, null=True, blank=True)
    
def __str__(self):
        return self.SubjectName
    



    
# Teacher details table
class TeacherTable(models.Model):
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    SubjectName = models.ManyToManyField(SubjectsTable, related_name='teachers', blank=True)
    LOGIN = models.ForeignKey(LoginTable, on_delete=models.CASCADE, null=True, blank=True)
    TeacherName = models.CharField(max_length=50, null=True, blank=True)
    Gender = models.CharField(max_length=50, null=True, blank=True)
    Phone_number = models.BigIntegerField(null=True, blank=True)
    Email = models.CharField(max_length=50, null=True, blank=True)
    Qualification = models.CharField(max_length=50, null=True, blank=True)


    
    
# Class information table
class ClassTable(models.Model):
    CType = [
        ('Class Room', 'Class Room'),
        ('Computer Lab', 'Computer Lab'),
        ('Electronics Lab', 'Electronics Lab'),
        ('Physics Lab', 'Physics Lab'),
        ('Chemistry Lab', 'Chemistry Lab'),
        ('Biology Lab', 'Biology Lab'),
        ('Maths Lab', 'Maths Lab'),
        ('Library', 'Library'),
        ('Auditorium', 'Auditorium'),
        ('Seminar Hall', 'Seminar Hall'),
    ]
    Semester = models.ForeignKey(SemesterTable, on_delete=models.CASCADE, null=True, blank=True)
    TeacherName = models.ForeignKey(TeacherTable, on_delete=models.CASCADE, null=True, blank=True)
    ClassName = models.CharField(max_length=50, null=True, blank=True)
    ClassType = models.CharField(max_length=50, choices=CType, null=True, blank=True)
    Latitude = models.CharField(max_length=50, null=True, blank=True)
    Longitude = models.CharField(max_length=50, null=True, blank=True)
    Location_name = models.CharField(max_length=50, null=True, blank=True) 
    Radius = models.IntegerField(null=True, blank=True)



# Student information table
class StudentTable(models.Model):
    Register_no = models.CharField(max_length=50, null=True, blank=True)
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    Semester = models.ForeignKey(SemesterTable, on_delete=models.CASCADE, null=True, blank=True)
    LOGIN = models.ForeignKey(LoginTable, on_delete=models.CASCADE, null=True, blank=True)
    ClassName = models.ForeignKey(ClassTable, on_delete=models.CASCADE, null=True, blank=True)
    StudentName = models.CharField(max_length=50, null=True, blank=True)
    Admission_no = models.CharField(max_length=50, null=True, blank=True)
    BatchYear = models.CharField(max_length=50, null=True, blank=True)
    Age = models.IntegerField(null=True, blank=True)
    Gender = models.CharField(max_length=50, null=True, blank=True)
    CourseName = models.ForeignKey(CourseTable, on_delete=models.CASCADE, null=True, blank=True)
    Date_of_birth = models.DateField(null=True, blank=True)
    Blood_group = models.CharField(max_length=50, null=True, blank=True)
    Guardian_name = models.CharField(max_length=50, null=True, blank=True)
    Guardian_relation = models.CharField(max_length=50, null=True, blank=True)
    Guardian_phone = models.BigIntegerField(null=True, blank=True)
    Email = models.CharField(max_length=50, null=True, blank=True)
    Address = models.CharField(max_length=50, null=True, blank=True)
    Phone_number = models.BigIntegerField(null=True, blank=True)


# Attendance records table
class AttendanceTable(models.Model):
    StudentName = models.ForeignKey(StudentTable, on_delete=models.CASCADE, null=True, blank=True)
    Date = models.DateField(null=True, blank=True)
    Period = models.CharField(max_length=50, null=True, blank=True)
    Status = models.CharField(max_length=50, null=True, blank=True)
    Attendance = models.IntegerField(null=True, blank=True)


# Class timetable table


# Timetable Entry
class TimeTableTable(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),  # Added Saturday
    ]

    ClassName = models.ForeignKey(ClassTable, on_delete=models.CASCADE, null=True, blank=True)
    SubjectName = models.ForeignKey(SubjectsTable, on_delete=models.CASCADE, null=True, blank=True)
    TeacherName = models.ForeignKey(TeacherTable, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(choices=DAYS_OF_WEEK, max_length=9 , null=True, blank=True)
    period = models.PositiveIntegerField(null=True, blank=True)  # E.g., 1st period, 2nd period, etc.
    start_time = models.TimeField( null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('ClassName', 'day', 'period')  # Prevents duplicate entries for the same class/period/day

    def __str__(self):
        return f"{self.ClassName} - {self.SubjectName} - {self.TeacherName} ({self.day}, Period {self.period})"



# Geographic location table
class LocationTable(models.Model):
    location_name = models.CharField(max_length=255, null=True, blank=True)
    polygon_coordinates = models.JSONField(null=True, blank=True)  # Stores multiple lat/lng points as JSON

    def __str__(self):
        return self.location_name


# Study notes table
class NotesTable(models.Model):
    SubjectName = models.ForeignKey(SubjectsTable, on_delete=models.CASCADE, null=True, blank=True)
    Teacher = models.ForeignKey(TeacherTable, on_delete=models.CASCADE, null=True, blank=True)
    Class_name = models.ForeignKey(ClassTable, on_delete=models.CASCADE, null=True, blank=True)
    Unit = models.CharField(max_length=50, null=True, blank=True)
    Notes = models.CharField(max_length=50, null=True, blank=True)

# Leave applications table
class LeaveApplicationTable(models.Model):
    StudentName = models.ForeignKey(StudentTable, on_delete=models.CASCADE, null=True, blank=True)
    Date = models.DateField(null=True, blank=True)
    Reason = models.CharField(max_length=50, null=True, blank=True)
    Status = models.CharField(max_length=50, null=True, blank=True)


# Student Notices Table
class StudentNoticeTable(models.Model):
    NTYPE = (
        ('HN', 'Holiday Notice'),
        ('EN', 'Exam Notice'),
        ('FN', 'Function Notice'),
        ('ON', 'Other Notice'),
    )
    
    Notice_name = models.CharField(max_length=200, null=True, blank=True)
    Notice_Type = models.CharField(max_length=100,null=True, blank=True ,choices=NTYPE)
    Notice_Content = models.TextField(max_length=1000, null=True, blank=True)
    File_Attachment = models.FileField(upload_to='notices/', null=True, blank=True)

    Date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.Notice_name

# Teacher Notices Table
class TeacherNoticeTable(models.Model):
    NoticeName = models.CharField(max_length=50, null=True, blank=True)
    NoticeContent = models.CharField(max_length=50, null=True, blank=True)
    Date = models.DateField(auto_now_add=True, null=True, blank=True)
    FileAttachment = models.FileField(upload_to='File/', null=True, blank=True)
    Department = models.ManyToManyField(DepartmentsTable)

    def __str__(self):
        return self.NoticeName
    

class CollegeDetailsTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)  # link to the User model
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    principal_name = models.CharField(max_length=100)
    principal_contact = models.CharField(max_length=15)
    # other fields...

    def __str__(self):
        return self.name