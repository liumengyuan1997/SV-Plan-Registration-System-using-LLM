from django.shortcuts import render, get_object_or_404

# Create your views here.

from .models import Employee, Order, Customer, Employees, Odetail, Part, Zipcode

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import connection

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

