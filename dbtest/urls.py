"""
URL configuration for dbtest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from dbapp import views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path('', views.testmysql),
    path('list/', views.EmployeeList.as_view(), name='employee_list'),
    path('list/<int:pk>', views.EmployeeDetail.as_view(), name='employee_detail'),
    path('create', views.EmployeeCreate.as_view() ),
    path('update/<int:pk>', views.EmployeeUpdate.as_view(), name='employee_update'),
    path('delete/<int:pk>', views.EmployeeDelete.as_view(), name='employee_delete'),
    path('order/', views.OrderList.as_view(), name='order_list'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]
