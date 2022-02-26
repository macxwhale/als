import imp
from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense, Float
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
import datetime
from django.db.models import Count, Sum, F
import decimal



def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            expense_name__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        # querry sets
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
   
    context = {
        'categories': categories,
        # saving values
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)
    # The view to handle the form POST requests
    if request.method == 'POST':
        # To check the amount, description have been entered
        amount = request.POST['amount']


        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        

        description = request.POST['description']
        expense_name = request.POST['expense_name']
        date = request.POST['expense_date']
        # category = request.POST['category']
        category = Category.objects.get(id=request.POST['category'])

      

        # Check if amount is greater than allocated float or float balance
        float_sum = Float.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum']
        expense_sum = Expense.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
    

        if not float_sum:
            messages.error(request, 'Please add Float for ' + category.name + ' before adding Expenses')
            return render(request, 'expenses/add_expense.html', context)
        else:
            balance = float_sum - expense_sum
            if decimal.Decimal(amount) > float_sum:
                messages.error(request, 'Expense amount cannot be more than the allocated amount of ' + str(float_sum))
                return render(request, 'expenses/add_expense.html', context)
        

            elif decimal.Decimal(amount) > balance:
                messages.error(request, 'Expense amount cannot be more than the float balance of ' + str(balance))
                return render(request, 'expenses/add_expense.html', context)
        

            if not date:
                messages.error(request, 'date is required')
                return render(request, 'expenses/add_expense.html', context)

            if not expense_name:
                messages.error(request, 'name is required')
                return render(request, 'expenses/add_expense.html', context)
            if not description:
                messages.error(request, 'description is required')
                return render(request, 'expenses/add_expense.html', context)
            # if no error we save the data into database
            # we use the expense model
            # create the expense
            Expense.objects.create(owner=request.user, amount=amount, date=date,
                                category=category, expense_name=expense_name, description=description)

            # saving the expense in the database after creating it
            messages.success(request, 'Expense saved successfully')

            # redirect to the expense page to see the expenses
            return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.exclude(id=expense.category.id)
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }


    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense_name = request.POST['expense_name']

        description = request.POST['description']

        date = request.POST['expense_date']
        
        category = Category.objects.get(id=request.POST['category'])

        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expenses/edit-expense.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        if not expense_name:
            messages.error(request, 'Expense name is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.expense_name = expense_name

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted')
    return redirect('expenses')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    one_months_ago = todays_date - datetime.timedelta(days=30 * 1)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=one_months_ago, date__lte=todays_date)
    # empty dictionary
    finalrep = {}

    def get_category(expense):
        return expense.category

    # we use map function
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    category_expenses = Expense.objects.annotate(name=F('category__name')).filter(amount__gt=0).values('name').annotate(category_expense_count=Count('id'), category_expense_sum=Sum('amount'))
    context = { 'category_expenses': category_expenses }
    return render(request, 'expenses/stats.html', context)

def float(request):
    floats = Float.objects.all()
    paginator = Paginator(floats, 20)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {
        'floats': floats,
        'page_obj': page_obj,
    }
    return render(request, 'expenses/float.html', context)


def add_float(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        # saving values
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_float.html', context)
    # The view to handle the form POST requests
    if request.method == 'POST':
        # To check the amount, description have been entered
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_float.html', context)

        description = request.POST['description']
        float_name = request.POST['float_name']
        date = request.POST['float_date']
        # category = request.POST['category']
        category = Category.objects.get(id=request.POST['category'])

        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expenses/add_float.html', context)

        if not float_name:
            messages.error(request, 'name is required')
            return render(request, 'expenses/add_float.html', context)
        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_float.html', context)
        # if no error we save the data into database
        # we use the expense model
        # create the expense
        Float.objects.create(amount=amount, date=date,
                               category=category, float_name=float_name, description=description)

        # saving the expense in the database after creating it
        messages.success(request, 'Float saved successfully')

        # redirect to the expense page to see the expenses
        return redirect('float')



def float_edit(request, id):
    float = Float.objects.get(pk=id)
    categories = Category.objects.exclude(id=float.category.id)
    context = {
        'float': float,
        'values': float,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-float.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-float.html', context)
        float_name = request.POST['float_name']
        description = request.POST['description']
        date = request.POST['float_date']
        category = Category.objects.get(id=request.POST['category'])

        if not date:
            messages.error(request, 'date is required')
            return render(request, 'expenses/edit-float.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-float.html', context)

        if not float_name:
            messages.error(request, 'Float name is required')
            return render(request, 'expenses/edit-float.html', context)

    #   expense.owner = request.user
        float.amount = amount
        float.date = date
        float.category = category
        float.description = description
        float.float_name = float_name

        float.save()
        messages.success(request, 'Float updated  successfully')

        return redirect('float')



def delete_float(request, id):
    float = Float.objects.get(pk=id)
    float.delete()
    messages.success(request, 'Float deleted')
    return redirect('float')

def category(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {
        'expenses': categories,
        'page_obj': page_obj,
    }
    return render(request, 'expenses/category.html', context)

def add_category(request):
   
    context = {
        # saving values
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_category.html', context)
    # The view to handle the form POST requests
    if request.method == 'POST':
      

        category_name = request.POST['category_name']
       

        if not category_name:
            messages.error(request, 'name is required')
            return render(request, 'expenses/add_category.html', context)
       
        # if no error we save the data into database
        # we use the expense model
        # create the expense
        Category.objects.create(name=category_name)

        # saving the expense in the database after creating it
        messages.success(request, 'Category saved successfully')

        # redirect to the expense page to see the expenses
        return redirect('category')

def category_edit(request, id):
    category = Category.objects.get(pk=id)

    context = {
        'category': category,
        'values': category
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit-category.html', context)
    if request.method == 'POST':
     
        category_name = request.POST['category_name']
        
        if not category_name:
            messages.error(request, 'Category name is required')
            return render(request, 'expenses/edit-category.html', context)

    #   expense.owner = request.user
        category.name = category_name

        category.save()
        messages.success(request, 'Category updated  successfully')

        return redirect('category')

    
def delete_category(request, id):
    category = Category.objects.get(pk=id)
    category.delete()
    messages.success(request, 'Category deleted')
    return redirect('category')

