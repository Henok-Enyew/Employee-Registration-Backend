# Generated by Django 3.2.25 on 2025-03-25 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='position',
            field=models.CharField(default='Unknown', max_length=40),
        ),
    ]
