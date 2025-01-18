from django.db import models

# User login table
class LoginTable(models.Model):
    UType = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('class_teacher', 'Class Teacher'),
    ]
    
    Username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    Password = models.CharField(max_length=50, null=True, blank=True)
    Type = models.CharField(max_length=50, choices=UType, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)



#department details table
class DepartmentsTable(models.Model):
    department_id = models.IntegerField(null=False, blank=False)
    Department = models.CharField(max_length=50, null=True, blank=True)
    CourseName = models.ForeignKey('CourseTable', on_delete=models.CASCADE, null=True, blank=True)
# Teacher details table
class TeacherTable(models.Model):
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    SubjectName = models.ForeignKey('SubjectsTable', on_delete=models.CASCADE, null=True, blank=True)
    LOGIN = models.ForeignKey(LoginTable, on_delete=models.CASCADE, null=True, blank=True)
    TeacherName = models.CharField(max_length=50, null=True, blank=True)
    Gender = models.CharField(max_length=50, null=True, blank=True)
    
    Phone_number = models.BigIntegerField(null=True, blank=True)
    Email = models.CharField(max_length=50, null=True, blank=True)
    Qualification = models.CharField(max_length=50, null=True, blank=True)

# Batch details table
class BatchTable(models.Model):
    ClassName = models.ForeignKey('ClassTable', on_delete=models.CASCADE, null=True, blank=True)
    BatchName = models.CharField(max_length=50, null=True, blank=True)
    BatchYear = models.CharField(max_length=50, null=True, blank=True)
    BatchStartYear = models.CharField(max_length=50, null=True, blank=True)
    BatchEndYear = models.CharField(max_length=50, null=True, blank=True)
    
    

# Semester details table
class SemesterTable(models.Model):
    BatchName = models.ForeignKey(BatchTable, on_delete=models.CASCADE, null=True, blank=True)
    Semester = models.CharField(max_length=50, null=True, blank=True)
    StartDate = models.DateField(null=True, blank=True)
    EndDate = models.DateField(null=True, blank=True)

# Class information table
class ClassTable(models.Model):
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    TeacherName = models.ForeignKey(TeacherTable, on_delete=models.CASCADE, null=True, blank=True)
    ClassName = models.CharField(max_length=50, null=True, blank=True)
    Latitude = models.CharField(max_length=50, null=True, blank=True)
    Longitude = models.CharField(max_length=50, null=True, blank=True)
    Location_name = models.CharField(max_length=50, null=True, blank=True)    
    Year = models.CharField(max_length=50, null=True, blank=True)
    Semester = models.ForeignKey(SemesterTable, on_delete=models.CASCADE, null=True, blank=True)

# Student information table
class StudentTable(models.Model):
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    Semester = models.ForeignKey(SemesterTable, on_delete=models.CASCADE, null=True, blank=True)
    LOGIN = models.ForeignKey(LoginTable, on_delete=models.CASCADE, null=True, blank=True)
    ClassName = models.ForeignKey(ClassTable, on_delete=models.CASCADE, null=True, blank=True)
    StudentName = models.CharField(max_length=50, null=True, blank=True)
    Admission_no = models.CharField(max_length=50, null=True, blank=True)
    BatchYear = models.CharField(max_length=50, null=True, blank=True)
    Age = models.IntegerField(null=True, blank=True)
    Gender = models.CharField(max_length=50, null=True, blank=True)
    CourseName = models.ForeignKey('SubjectsTable', on_delete=models.CASCADE, null=True, blank=True)
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
    Status = models.CharField(max_length=50, null=True, blank=True)
    Attendance = models.IntegerField(null=True, blank=True)


# Subject details table
class SubjectsTable(models.Model): 
    Subject_code = models.CharField(max_length=50, null=True, blank=True)
    SubjectName = models.CharField(max_length=50, null=True, blank=True)
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)
    Course = models.ForeignKey('CourseTable', on_delete=models.CASCADE, null=True, blank=True)
    Year_of_Syllabus = models.DateField(null=True, blank=True)
    Semester = models.ForeignKey(SemesterTable, on_delete=models.CASCADE, null=True, blank=True)
    
    
#course details table
class CourseTable(models.Model):
    CourseName = models.CharField(max_length=50, null=True, blank=True)
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)

# Class timetable table


class TimeTableTable(models.Model):
    ClassName = models.ForeignKey(ClassTable, on_delete=models.CASCADE, null=True, blank=True)
    SubjectName = models.ForeignKey(SubjectsTable, on_delete=models.CASCADE, null=True, blank=True)
    Day = models.CharField(max_length=10, null=True, blank=True)
    Period = models.CharField(max_length=20, null=True, blank=True)
    StartTime = models.TimeField(max_length=50, null=True, blank=True)
    EndTime = models.TimeField(max_length=50, null=True, blank=True)
    TeacherName = models.ForeignKey(TeacherTable, on_delete=models.CASCADE, null=True, blank=True)
    # No custom methods like __str__ here


# Geographic location table
class LocationTable(models.Model):
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    Location_name = models.CharField(max_length=50, null=True, blank=True)


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

# Student notices table


# Student Notices Table
class StudentNoticeTable(models.Model):
    Notice_name = models.CharField(max_length=200, null=True, blank=True)
    Notice_Content = models.TextField(max_length=1000, null=True, blank=True)
    File_Attachment = models.FileField(upload_to='notices/', null=True, blank=True)
    BatchName = models.ManyToManyField(BatchTable,)  # Many-to-many relationship
    Date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.Notice_name

# Teacher Notices Table
class TeacherNoticeTable(models.Model):
    NoticeName = models.CharField(max_length=50, null=True, blank=True)
    NoticeContent = models.CharField(max_length=50, null=True, blank=True)
    Date = models.DateField(auto_now_add=True, null=True, blank=True)
    FileAttachment = models.FileField(upload_to='File/', null=True, blank=True)
    Department = models.ForeignKey(DepartmentsTable, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.NoticeName
    

class CollegeDetailsTable(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    principal_name = models.CharField(max_length=255, null=False, blank=False)
    principal_contact = models.CharField(max_length=15, null=False, blank=False)

    def __str__(self):
        return self.name