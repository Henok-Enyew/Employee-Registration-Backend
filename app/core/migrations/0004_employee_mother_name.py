# Generated by Django 3.2.25 on 2025-04-11 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_employeefamily'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='mother_name',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
