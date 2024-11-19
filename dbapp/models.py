# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Task(models.Model):
    taskId = models.AutoField(blank=True, primary_key=True)
    studentId = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    entryDate = models.DateField(blank=True, null=True)
    dueDate = models.DateField(blank=True, null=True)
    class Meta:
        # managed = False
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
        # managed = False
        db_table = 'files'

class Department(models.Model):
    dnumber = models.IntegerField(blank=True, null=True)
    dname = models.CharField(max_length=15, blank=True, null=True)
    mgr_ssn = models.CharField(max_length=9, blank=True, null=True)
    mgr_start_date = models.DateField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'department'


class Employee(models.Model):
    fname = models.CharField(max_length=8, blank=True, null=True)
    minit = models.CharField(max_length=2, blank=True, null=True)
    lname = models.CharField(max_length=8, blank=True, null=True)
    ssn = models.CharField(primary_key=True, max_length=9)
    bdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=27, blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    salary = models.IntegerField()
    super_ssn = models.CharField(max_length=9, blank=True, null=True)
    dno = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'employee'


class Employees(models.Model):
    eno = models.IntegerField(primary_key=True)
    ename = models.CharField(max_length=18)
    zip = models.CharField(max_length=6)
    hdate = models.DateField()
    class Meta:
        # managed = False
        db_table = 'employees'

class Part(models.Model):
    pno = models.IntegerField(primary_key=True)
    pname = models.CharField(max_length=30)
    qoh = models.IntegerField()
    prices = models.DecimalField(max_digits=6, decimal_places=2)
    wlevel = models.IntegerField()
    class Meta:
        # managed = False
        db_table = 'parts'

class Customer(models.Model):
    cno = models.IntegerField(primary_key=True)
    cname = models.CharField(max_length=18)
    street = models.CharField(max_length=30)
    zip = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    class Meta:
        # managed = False
        db_table = 'customers'

class Order(models.Model):
    ono = models.IntegerField(primary_key=True)
    cno = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='cno')
    eno = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='eno')
    received = models.DateField()
    shipped = models.DateField(null=True, blank=True)
    class Meta:
        # managed = False
        db_table = 'orders'

class Odetail(models.Model):
    ono = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='ono', primary_key=True)
    pno = models.ForeignKey(Part, on_delete=models.CASCADE, db_column='pno')
    qty = models.IntegerField()
    class Meta:
        # managed = False
        db_table = 'odetails'

class Zipcode(models.Model):
    zip = models.CharField(max_length=6, primary_key=True)
    city = models.CharField(max_length=15)
    class Meta:
        # managed = False
        db_table = 'zipcodes'

