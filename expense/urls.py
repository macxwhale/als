from django.urls import path
from . import views

urlpatterns = [
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
    path('add-expense', views.add_expense, name="add-expense"),
    path('edit-expense/<int:id>', views.edit_expense, name="edit-expense"),
    path('delete-expense/<int:id>', views.delete_expense, name="delete-expense"),

    # Reports
    path('float-vs-expense', views.float_vs_expense, name="float-vs-expense"),
    path('user-expense', views.user_expense, name="user-expense"),
]
