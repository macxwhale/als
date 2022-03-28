from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('sign-in', views.sign_in, name="sign-in"),
    path('sign-out/', views.sign_out, name="sign-out"),
    path('', views.index, name="index"),

    # Stations
    path('stations', views.stations, name="stations"),
    path('add-station', views.add_station, name="add-station"),
    path('edit-station/<int:id>', views.edit_station, name="edit-station"),
    path('delete-station/<int:id>', views.delete_station, name="delete-station"),

    # Float
    path('float', views.float, name="float"),
    path('add-float', views.add_float, name="add-float"),
    path('edit-float/<int:id>', views.edit_float, name="edit-float"),
    path('delete-float/<int:id>', views.delete_float, name="delete-float"),

    # Expense
    path('expense', views.expense, name="expense"),
    path('my-expense', views.my_expense, name="my-expense"),
    path('add-expense', views.add_expense, name="add-expense"),
    path('edit-expense/<int:id>', views.edit_expense, name="edit-expense"),
    path('delete-expense/<int:id>', views.delete_expense, name="delete-expense"),

    # User
    path('users', views.users, name="users"),
    path('add-user', views.add_user, name="add-user"),
    path('edit-user/<int:id>', views.edit_user, name="edit-user"),
    path('delete-user/<int:id>', views.delete_user, name="delete-user"),

    # Reports
    path('float-vs-expense', views.float_vs_expense, name="float-vs-expense"),
    path('user-expense', views.user_expense, name="user-expense"),
    path('all-user-expense', views.all_user_expense, name="all-user-expense"),
    path('user-expense-advanced-reports', views.user_expense_advanced_reports, name="user-expense-advanced-reports"),
    path('float-vs-expense-advanced-reports', views.float_vs_expense_advanced_reports, name="float-vs-expense-advanced-reports"),
]
