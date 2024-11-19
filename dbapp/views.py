from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

from .models import Employee, Order, Customer, Employees, Odetail, Part, Zipcode, UploadedFile, Task

from django import forms
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.db import connection
from django.utils.timezone import now
from datetime import datetime

from .utils import process_file_content, generate_task_description_and_due_date
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('file',)

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file = uploaded_file.file

            content = process_file_content(file)
            if content:
                task_description, due_date = generate_task_description_and_due_date(content)

                task = Task.objects.create(
                    studentId=None,  # todo: after add student table
                    description=task_description,
                    entryDate=now().date(),
                    dueDate=due_date
                )

                uploaded_file.taskId = task
                uploaded_file.save()

                return JsonResponse({
                    'message': 'Task and file created successfully.',
                    'task': {
                        'taskId': task.taskId,
                        'description': task.description,
                        'entryDate': task.entryDate,
                        'dueDate': task.dueDate
                    },
                    'file': {
                        'fileId': uploaded_file.fileId,
                        'filePath': uploaded_file.file.url
                    }
                })
            else:
                return JsonResponse({'error': 'Unsupported file type'}, status=400)

def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'GET':
        uploaded_file = UploadedFile.objects.filter(taskId=task).first()

        return JsonResponse(
            {
                'taskId': task.taskId,
                'description': task.description,
                'entryDate': task.entryDate,
                'dueDate': task.dueDate,
                'file': None if not uploaded_file else {
                    'fileId': uploaded_file.fileId,
                    'filePath': uploaded_file.file.url
                }
            }
        )

def update_task(request, task_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    task = get_object_or_404(Task, pk=task_id)

    description = request.POST.get('description')
    due_date = request.POST.get('dueDate')

    if description:
        task.description = description
    if due_date:
        try:
            task.dueDate = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    task.save()

    return JsonResponse({
        'taskId': task.taskId,
        'description': task.description,
        'dueDate': task.dueDate,
        'studentId': task.studentId,
        'entryDate': task.entryDate,
    })

def task_detail_data(task_id):
    """Helper function to get task detail data."""
    task = get_object_or_404(Task, pk=task_id)
    uploaded_file = UploadedFile.objects.filter(taskId=task).first()

    return {
        'taskId': task.taskId,
        'description': task.description,
        'entryDate': task.entryDate.strftime('%Y-%m-%d') if task.entryDate else None,
        'dueDate': task.dueDate.strftime('%Y-%m-%d') if task.dueDate else None,
        'file': None if not uploaded_file else {
            'fileId': uploaded_file.fileId,
            'filePath': uploaded_file.file.url
        }
    }

def all_tasks(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)

    # Get all tasks
    tasks = Task.objects.all()

    # Generate detailed data for all tasks
    tasks_data = [task_detail_data(task.taskId) for task in tasks]

    return JsonResponse({'tasks': tasks_data})

def testmysql(request):
    employee = Employee.objects.all()
    context = {
    'user_ssn': employee[0].ssn,
    'user_name': employee[0].lname,
    }
    return render(request, 'home.html', context)


class EmployeeList(ListView):
    template_name='dbapp/employee_list.html' 
    model = Employee

class EmployeeDetail(DetailView):
    model = Employee

class EmployeeCreate(CreateView):
    model = Employee
    fields = [
        'fname',
        'minit',
        'lname',
        'ssn',
        'bdate',
        'address',
        'sex',
        'salary',
        'super_ssn',
        'dno',
    ]
    #template_name_suffix = '_update_form' 
    success_url = "/list"

class EmployeeUpdate(UpdateView):
    model = Employee
    fields = [
        'fname',
        'minit',
        'lname',
        'ssn',
        'bdate',
        'address',
        'sex',
        'salary',
        'super_ssn',
        'dno',
    ]
    #template_name_suffix = '_update_form'
    success_url = "/list"

class EmployeeDelete(DeleteView):
    model = Employee
    success_url = "/list"


class OrderList(ListView):
    template_name='dbapp/order_list.html' 
    model = Order

class OrderDetailView(DetailView):
    model = Order
    template_name = 'dbapp/order_details.html'  # Specify your template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()

        # Retrieve related customer and employee info
        customer = order.cno
        employee = order.eno
        zip_info = Zipcode.objects.filter(zip=customer.zip).first()

        # Get order details and parts information
        order_details = Odetail.objects.filter(ono=order)
        parts = []
        total_order_sum = 0

        for detail in order_details:
            part = detail.pno
            quantity = detail.qty
            price = part.prices
            part_sum = quantity * price
            total_order_sum += part_sum
            parts.append({
                'part_no': part.pno,
                'part_name': part.pname,
                'quantity': quantity,
                'price': price,
                'sum': part_sum,
            })

        # Add custom data to the context
        context.update({
            'customer': customer,
            'customer_no': customer.cno,
            'zip_code': customer.zip,
            'city': zip_info.city if zip_info else None,
            'taken_by': employee.ename,
            'received_on': order.received,
            'shipped_on': order.shipped,
            'parts': parts,
            'total': total_order_sum,
        })
        return context

