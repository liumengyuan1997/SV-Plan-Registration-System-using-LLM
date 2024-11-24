from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Admin', 'Admin')
    ]

    DEPARTMENT_CHOICES = [
        ('Khoury', 'Khoury'),
        ('COE', 'COE')
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Student')
    created_at = models.DateTimeField(auto_now_add=True)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, default='Khoury')
    
    class Meta:
        managed = True
        db_table = 'dbapp_user'

    def __str__(self):
        return self.email

class Task(models.Model):
    class TaskStatus(models.TextChoices):
        IN_PROCESS = 'In process', 'In process'
        COMPLETED = 'Completed', 'Completed'
        PENDING = 'Overdue', 'Overdue'
    class TaskCategory(models.TextChoices):
        COURSE = 'Course', 'Course'
        DAILY_SCHEDULE = 'DailySchedule', 'DailySchedule'
        RESEARCH = 'Research', 'Research'
        MEETING = 'Meeting', 'Meeting'
    taskId = models.AutoField(blank=True, primary_key=True)
    taskName = models.CharField(max_length=255)
    studentEmail = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='email',
        to_field='email'
    )
    description = models.TextField(blank=True, null=True)
    entryDate = models.DateField(blank=True, null=True)
    dueDate = models.DateField(blank=True, null=True)
    taskStatus = models.CharField(max_length=50, choices=TaskStatus.choices, default=TaskStatus.IN_PROCESS, null=False, blank=False)
    taskCategory = models.CharField(max_length=50, choices=TaskCategory.choices, default=TaskCategory.DAILY_SCHEDULE, null=False, blank=False)

    class Meta:
        managed = True
        db_table = 'tasks'

class UploadedFile(models.Model):
    fileId = models.AutoField(blank=True, primary_key=True)
    file = models.FileField(upload_to='uploads/')
    # foreign key
    taskId = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        db_column='taskId',
        to_field='taskId',
        blank=True,
        null=True 
    )
    class Meta:
        managed = True
        db_table = 'files'

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Workshop', 'Workshop'),
        ('Career Fair', 'Career Fair'),
        ('Conference', 'Conference'),
        ('Culture Festival', 'Culture Festival'),
        ('Volunteer', 'Volunteer'),
        ('Opportunity', 'Opportunity'),
    ]

    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=255)
    event_description = models.TextField()
    event_location = models.CharField(max_length=255)
    event_time = models.DateTimeField()
    event_published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_column='event_published_by'
    )
    event_created_at = models.DateTimeField(auto_now_add=True)
    event_status = models.CharField(max_length=50, default='Upcoming', null=False, blank=False)
    event_category = models.CharField(max_length=50,choices=CATEGORY_CHOICES, default='Conference')

    def __str__(self):
        return self.event_name
