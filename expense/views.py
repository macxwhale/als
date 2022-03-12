
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pytz import timezone
from .models import *
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.db.models import Count, Sum, F
from django.db import connection
from django.utils.dateparse import parse_datetime

from .functions import dictfetchall


def index(request):
    context = {}
    return render(request, 'expense/index.html', context)

""" Station """
def stations(request):
    stations = Station.objects.all()
    context = {'stations': stations, }
    return render(request, 'expense/station/stations.html', context)

def add_station(request):

    context = {'values': request.POST }

    if request.method == 'GET':
        return render(request, 'expense/station/add-station.html', context)

    # The view to handle the form POST requests
    if request.method == 'POST':
      
        station_name = request.POST['station_name']

        if not station_name:
            messages.error(request, 'name is required')
            return render(request, 'expense/station/add-station.html', context)
       
        # if no error we save the data into database
        # we use the expense model
        # create the expense
        Station.objects.create(name=station_name, created_by=request.user)

        # saving the expense in the database after creating it
        messages.success(request, 'Sations saved successfully')

        # redirect to the expense page to see the expenses
        return redirect('stations')

def edit_station(request, id):
    station = Station.objects.get(pk=id)

    context = {
        'station': station,
        'values': station
    }

    if request.method == 'GET':
        return render(request, 'expense/station/edit-station.html', context)

    if request.method == 'POST':
     
        station_name = request.POST['station_name']
        
        if not station_name:
            messages.error(request, 'Station name is required')
            return render(request, 'expense/station/edit-station.html', context)

        station.name = station_name
        station.created_by = station.created_by
        station.created_on = station.created_on

        station.save()
        messages.success(request, 'Station updated  successfully')

        return redirect('stations')

def delete_station(request, id):
    station = Station.objects.get(pk=id)
    station.delete()
    messages.success(request, 'Station deleted')
    return redirect('stations')

""" Station """

""" Float """
def float(request):
    floats = Float.objects.all()
    context = {
        'floats': floats,
    }
    return render(request, 'expense/float/float.html', context)

def add_float(request):
    stations = Station.objects.all()
    context = {
        'stations': stations,
        'values': request.POST
    }

    print(request.POST)
   
    if request.method == 'GET':
        return render(request, 'expense/float/add-float.html', context)
    # The view to handle the form POST requests
    if request.method == 'POST':
        # To check the amount, description have been entered
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expense/float/add-float.html', context)

        description = request.POST['description']
    
        date = request.POST['float_date']


        station = Station.objects.get(id=request.POST['station'])
        
        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expense/float/add-float.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expense/float/add-float.html', context)
        # if no error we save the data into database
        # we use the expense model
        # create the expense
        Float.objects.create(amount=amount, date=date,
                               station=station, description=description,  created_by=request.user)

        # saving the expense in the database after creating it
        messages.success(request, 'Float saved successfully')

        # redirect to the expense page to see the expenses
        return redirect('float')

def edit_float(request, id):
    float = Float.objects.get(pk=id)
    stations = Station.objects.exclude(id=float.station.id)
    context = {
        'float': float,
        'values': float,
        'stations': stations
    }

    if request.method == 'GET':
        return render(request, 'expense/float/edit-float.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expense/float/edit-float.html', context)
      
        description = request.POST['description']

        date = request.POST['float_date']


        station = Station.objects.get(id=request.POST['station'])

        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expense/float/edit-float.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'eexpense/float/edit-float.html', context)

        float.amount = amount
        float.date = date
        float.station = station
        float.description = description
        float.created_by = float.created_by
        float.created_on = float.created_on

        float.save()
        messages.success(request, 'Float updated  successfully')

        return redirect('float')

def delete_float(request, id):
    float = Float.objects.get(pk=id)
    float.delete()
    messages.success(request, 'Float deleted')
    return redirect('float')
""" Float End """

""" Expense """
def expense(request):
    expenses = Expense.objects.all()
    context = {
        'expenses': expenses,
    }
    return render(request, 'expense/expense/expenses.html', context)

def add_expense(request):
    stations = Station.objects.all()
    context = {
        'stations': stations,
        'values': request.POST
    }

    print(request.POST)
   
    if request.method == 'GET':
        return render(request, 'expense/expense/add-expense.html', context)
    # The view to handle the form POST requests
    if request.method == 'POST':
        # To check the amount, description have been entered
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expense/expense/add-expense.html', context)

        description = request.POST['description']
    
        date = request.POST['expense_date']


        station = Station.objects.get(id=request.POST['station'])

        expense_name = request.POST['expense_name']
        
        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expense/expense/add-expense.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expense/expense/add-expense.html', context)
        # if no error we save the data into database
        # we use the expense model
        # create the expense
        Expense.objects.create(created_by=request.user, amount=amount, date=date,
                            station=station, expense_name=expense_name, description=description)

        # saving the expense in the database after creating it
        messages.success(request, 'Expense saved successfully')

        # redirect to the expense page to see the expenses
        return redirect('expense')

def edit_expense(request, id):

    expense = Expense.objects.get(pk=id)
    stations = Station.objects.exclude(id=expense.station.id)
    context = {
        'expense': expense,
        'values': expense,
        'stations': stations
    }


    if request.method == 'GET':
        return render(request, 'expense/expense/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expense/expense/edit-expense.html', context)

        expense_name = request.POST['expense_name']

        description = request.POST['description']

        date = request.POST['expense_date']
        
        station = Station.objects.get(id=request.POST['station'])

        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expense/expense/edit-expense.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expense/expense/edit-expense.html', context)

        if not expense_name:
            messages.error(request, 'Expense name is required')
            return render(request, 'expense/expense/edit-expense.html', context)

        expense.amount = amount
        expense.date = date
        expense.station = station
        expense.description = description
        expense.expense_name = expense_name

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expense')

def delete_expense(request, id):
    float = Float.objects.get(pk=id)
    float.delete()
    messages.success(request, 'Float deleted')
    return redirect('float')

""" Expense End """

""" Reports """
def float_vs_expense(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, expense_station.name, (SELECT COALESCE(SUM(expense_float.amount), 0) from expense_float WHERE expense_float.station_id = expense_station.id) as float_sum, (SELECT COALESCE(SUM(expense_expense.amount), 0) from expense_expense WHERE expense_expense.station_id =  expense_station.id) as expense_sum FROM expense_station")
        results = dictfetchall(cursor)
    context = { 'results': results }
    return render(request, 'expense/reports/float-vs-expense.html', context)

def user_expense(request):
    user_expense = Expense.objects.annotate(username=F('created_by__username')).values('username').annotate(user_expense_sum=Sum('amount'))
    context = { 'user_expense': user_expense }
    return render(request, 'expense/reports/user-expense.html', context)
