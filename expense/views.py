
from venv import create
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pytz import timezone
from .models import *
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F
from django.db import connection
from .functions import dictfetchall
from datetime import datetime, timedelta, time
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users


@unauthenticated_user
def sign_in(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('index')

		else:
			messages.info(request, 'Username or password is incorrect')

	context = {}
	return render(request, 'expense/auth/sign-in.html', context)

def sign_out(request):
	logout(request)
	return redirect('sign-in')

@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def index(request):
    """ Get the current date """
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())
    
    month = today + timedelta(30)
    m_today_start = datetime.combine(today, time())
    m_today_end = datetime.combine(month, time())

    """ Get the current month """
    this_month = datetime.now().month
    last_month = datetime.now().month - 1


    """ User count """
    u_count = User.objects.count()
    
    """ Station count """
    s_count = Station.objects.count()

    """ Total Float """
    t_float = Float.objects.aggregate(Sum('amount'))['amount__sum']

    """ Total Expense """
    t_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum']

    """ Latest Expense """
    l_expense = Expense.objects.all().order_by('-created_on')[:7]

    """ This/Last month's float """
    f_this_month = Float.objects.filter(created_on__month=this_month).aggregate(Sum('amount'))['amount__sum']
    f_last_month = Float.objects.filter(created_on__month=last_month).aggregate(Sum('amount'))['amount__sum']

    """ This/Last month's Expense """
    e_this_month = Expense.objects.filter(created_on__month=this_month).aggregate(Sum('amount'))['amount__sum']
    e_last_month = Expense.objects.filter(created_on__month=last_month).aggregate(Sum('amount'))['amount__sum']


    """ Float Charts """
    fs_labels = []
    fs_data = []

    float_per_station_sum = Float.objects.values(name=F('station__name')).annotate(station_float_sum=Sum('amount')).order_by('-station_float_sum')[:5]

    for fss in float_per_station_sum:
        fs_labels.append(fss['name'])
        fs_data.append(str(fss['station_float_sum']))
    
    """ Expense Charts """
    es_labels = []
    es_data = []

    expense_per_station_sum = Expense.objects.values(name=F('station__name')).annotate(station_expense_sum=Sum('amount')).order_by('-station_expense_sum')[:5]

    for ess in expense_per_station_sum:
        es_labels.append(ess['name'])
        es_data.append(str(ess['station_expense_sum']))

    """ Float vs Expense """   
    fve_labels = []
    fve_float_sum = []
    fve_expense_sum = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, expense_station.name, (SELECT COALESCE(SUM(expense_float.amount), 0) from expense_float WHERE expense_float.station_id = expense_station.id) as float_sum, (SELECT COALESCE(SUM(expense_expense.amount), 0) from expense_expense WHERE expense_expense.station_id =  expense_station.id) as expense_sum FROM expense_station ORDER BY expense_sum DESC LIMIT 5")
        results = dictfetchall(cursor)
    
    for fve in results:
        fve_labels.append(fve['name'])
        fve_float_sum.append(str(fve['float_sum']))
        fve_expense_sum.append(str(fve['expense_sum']))
    
    """ User vs Float """
    ue5_labels = []
    ue5_expense_sum = []

    user_expense_per_station_sum = Expense.objects.values(name=F('created_by__username')).annotate(user_expense_sum=Sum('amount')).order_by('-user_expense_sum')[:5]

    for ue5 in user_expense_per_station_sum:
        ue5_labels.append(ue5['name'])
        ue5_expense_sum.append(str(ue5['user_expense_sum']))
   

    context = {
        'u_count':u_count,
        's_count':s_count,
        't_float':t_float,
        't_expense':t_expense,
        'l_expense':l_expense,
        'f_this_month':f_this_month,
        'f_last_month':f_last_month,
        'e_this_month':e_this_month,
        'e_last_month':e_last_month,
        'fs_labels': fs_labels,
        'fs_data': fs_data,
        'es_labels': es_labels,
        'es_data': es_data,
        'fve_labels':fve_labels,
        'fve_float_sum':fve_float_sum,
        'fve_expense_sum':fve_expense_sum,
        'ue5_labels': ue5_labels,
        'ue5_expense_sum':  ue5_expense_sum
        }
    return render(request, 'expense/index.html', context)

""" User """
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin'])
def users(request):
    users = User.objects.all()
    context = {'users': users }
    return render(request, 'expense/users/users.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin'])
def add_user(request):
    form = CreateUserForm()
    groups = Group.objects.all()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        email = request.POST['email']
       
        print('Printing POST:', request.POST)
        print('Printing Errors:', form.errors )
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        else:
            if form.is_valid():
                user = form.save()
                user.save()
            
                username = form.cleaned_data.get('username')
                g = form.cleaned_data.get('group')
            
                print('selected user role:',g)
                
                if g == 'SystemAdmin':
                    g = Group.objects.get(name='SystemAdmin')
                    g.user_set.add(user)
                elif g == 'SystemAccountant':
                    g = Group.objects.get(name='SystemAccountant')
                    g.user_set.add(user)
                elif g == 'SystemUser':
                    g = Group.objects.get(name='SystemUser')
                    g.user_set.add(user)
                else:
                    messages.error(request,  username + " cannot be added to a group")
                    return redirect('users')

                messages.success(request,  username + " has been created successfully")
                return redirect('users')

    
    context = {'groups': groups, 'form': form}
    return render(request, 'expense/users/add-user.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin'])
def edit_user(request, id):
    user = User.objects.get(pk=id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM `auth_group`")
        groups = dictfetchall(cursor)

    context = {
        'groups': groups, 
        'values': user
        }
    
    if request.method == 'GET':
        return render(request, 'expense/users/edit-user.html', context)

    if request.method == 'POST':
        e = request.POST['email']
        u = request.POST['username']
        usr = User.objects.exclude(pk=id).filter(email=e)

       
        if User.objects.exclude(pk=id).filter(email=e):
            messages.error(request, "Email already exists")
            return render(request, 'expense/users/edit-user.html', context)
        elif User.objects.exclude(pk=id).filter(username=u):
            messages.error(request, "Username already exists")
            return render(request, 'expense/users/edit-user.html', context)
        else:
            email = request.POST['email']
            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            g = request.POST['group']

            print('selected user role:',g)


            with connection.cursor() as cursor:
                cursor.execute("call sp_update_user(%s, %s, %s, %s, %s, %s)", (id, username, first_name, last_name, email, g))
                data = cursor.fetchone()
                messages.success(request,  username + " has been updated successfully")
                return redirect('users')
        
        

    return render(request, 'expense/users/edit-user.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin'])
def delete_user(request, id):
    with connection.cursor() as cursor:
        cursor.execute("call sp_delete_user(%s)", [id])
        data = cursor.fetchone()
        messages.success(request, 'User deleted')
        return redirect('users')

""" User End """

""" Station """
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def stations(request):
    stations = Station.objects.all()
    context = {'stations': stations, }
    return render(request, 'expense/station/stations.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
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
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
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
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def delete_station(request, id):
    station = Station.objects.get(pk=id)
    station.delete()
    messages.success(request, 'Station deleted')
    return redirect('stations')

""" Station """

""" Float """
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def float(request):
    floats = Float.objects.all()
    context = {
        'floats': floats,
    }
    return render(request, 'expense/float/float.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
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
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
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
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def delete_float(request, id):
    float = Float.objects.get(pk=id)
    float.delete()
    messages.success(request, 'Float deleted')
    return redirect('float')
""" Float End """

""" Expense """
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def expense(request):
    expenses = Expense.objects.all()
    context = {
        'expenses': expenses,
    }
    return render(request, 'expense/expense/expenses.html', context)

""" Expense """
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant', 'SystemUser'])
def my_expense(request):
    expenses = Expense.objects.filter(created_by = request.user)
    context = {
        'expenses': expenses,
    }
    return render(request, 'expense/expense/expenses.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant', 'SystemUser'])
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

        reciept = request.FILES['reciept']

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
                            station=station, expense_name=expense_name, description=description, reciept=reciept)

        # saving the expense in the database after creating it
        messages.success(request, 'Expense saved successfully')

        # redirect to the expense page to see the expenses
        return redirect('my-expense')
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant', 'SystemUser'])
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

       
        reciept = request.FILES['reciept']
       
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
        expense.reciept = reciept

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expense')
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant', 'SystemUser'])
def delete_expense(request, id):
    float = Float.objects.get(pk=id)
    float.delete()
    messages.success(request, 'Float deleted')
    return redirect('float')

""" Expense End """

""" Reports """
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def float_vs_expense(request):
    with connection.cursor() as cursor:
        cursor.execute("CALL sp_float_vs_expense_amount")
        results = dictfetchall(cursor)
    context = { 'results': results }
    return render(request, 'expense/reports/float-vs-expense.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant', 'SystemUser'])
def user_expense(request):
    # user_expense = Expense.objects.annotate(username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
    
    # SELECT COALESCE(SUM(amount), 0), station_id from expense_expense as expense_sum WHERE created_by_id = 1 GROUP BY station_id
    
    user_expense = Expense.objects.filter(created_by=request.user).values(name=F('station__name'), username=F('created_by__username')).annotate(user_expense_sum=Sum('amount')).order_by('-user_expense_sum')
    context = { 'user_expense': user_expense }
    return render(request, 'expense/reports/user-expense.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def all_user_expense(request):
    """ Get the current date """
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())
    # user_expense = Expense.objects.annotate(username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
    
    # SELECT COALESCE(SUM(amount), 0), station_id from expense_expense as expense_sum WHERE created_by_id = 1 GROUP BY station_id
    
    user_expense = Expense.objects.filter(created_on__range=(today_start, today_end)).values(name=F('station__name'), username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
    context = { 'user_expense': user_expense }
    return render(request, 'expense/reports/user-expense.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def user_expense_advanced_reports(request):
    users = User.objects.all()
    context = { 'users': users }
    # user_expense = Expense.objects.annotate(username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
    
    # SELECT COALESCE(SUM(amount), 0), station_id from expense_expense as expense_sum WHERE created_by_id = 1 GROUP BY station_id
    # user_expense = Expense.objects.filter(created_by=request.user).values(name=F('station__name'), username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))


    print(request.POST)

    if request.method == 'POST':
        user = request.POST['user']
        start = request.POST['start']
        start_date = datetime.strptime(start, "%m/%d/%Y").strftime("%Y-%m-%d")
        end = request.POST['end']
        end_date = datetime.strptime(end, "%m/%d/%Y").strftime("%Y-%m-%d")

        if user:
            if start_date == end_date:
                messages.error(request, 'Start Date and End Date are similar')
                return render(request, 'expense/reports/user-advanced-reports.html', context)
            else:
                user_expense = Expense.objects.filter(created_by=user, date__range=(start_date, end_date)).values(name=F('station__name'), username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
                context = { 'user_expense': user_expense,'users': users }
                return render(request, 'expense/reports/user-advanced-reports.html', context)

     
    return render(request, 'expense/reports/user-advanced-reports.html', context)
@login_required(login_url='sign-in')
@allowed_users(allowed_roles=['SystemAdmin', 'SystemAccountant'])
def float_vs_expense_advanced_reports(request):
    stations = Station.objects.all()
    context = { 'stations': stations }
    # user_expense = Expense.objects.annotate(username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
    
    # SELECT COALESCE(SUM(amount), 0), station_id from expense_expense as expense_sum WHERE created_by_id = 1 GROUP BY station_id
    # user_expense = Expense.objects.filter(created_by=request.user).values(name=F('station__name'), username=F('created_by__username')).annotate(user_expense_sum=Sum('amount'))
    # datetime.datetime.strptime("23 Mar, 2022", "%d/%m/%Y").strftime("%Y-%m-%d")

    print(request.POST)

    if request.method == 'POST':
        station = request.POST['station']
        if station:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, expense_station.name, (SELECT COALESCE(SUM(expense_float.amount), 0) from expense_float WHERE expense_float.station_id = expense_station.id) as float_sum, (SELECT COALESCE(SUM(expense_expense.amount), 0) from expense_expense WHERE expense_expense.station_id =  expense_station.id) as expense_sum FROM expense_station WHERE id = %s", [station])
                results = dictfetchall(cursor)
            context = { 'results': results, 'stations': stations }

        
    return render(request, 'expense/reports/float-advanced-reports.html', context)

""" Reports End """