# Generated by Django 5.0.4 on 2024-05-05 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_customuser_is_block'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='category',
        ),
    ]
