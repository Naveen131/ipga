# Generated by Django 5.0.6 on 2024-08-04 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_user_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='role',
            new_name='role_type',
        ),
        # migrations.AlterField(
        #     model_name='user',
        #     name='password',
        #     field=models.CharField(max_length=128, verbose_name='password'),
        # ),
    ]
