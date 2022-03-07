# Generated by Django 3.2 on 2022-03-04 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_alter_expense_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='float',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='float_category', to='expenses.category'),
        ),
    ]