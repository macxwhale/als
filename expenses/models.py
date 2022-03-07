from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import date
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=256)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    # how categories should be called in plural form we use Class Meta verbose_name_plural
    class Meta:
        verbose_name_plural = 'Categories'
        ordering: ['-id']

    def __str__(self):
        return self.name


# Create your models here.
class Expense(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField()
    description = models.TextField()
    expense_name = models.TextField(default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="expense_category")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category

    # to sort order
    class Meta:
        ordering: ['-date']

# Create your models here.
class Float(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="float_category")
    date = models.DateTimeField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category
