from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import date
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=256)

    # how categories should be called in plural form we use Class Meta verbose_name_plural
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# Create your models here.
class Expense(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField()
    description = models.TextField()
    expense_name = models.TextField(default=None)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.category

    # to sort order
    class Meta:
        ordering: ['-date', ]
