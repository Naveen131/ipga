# Generated by Django 5.0.6 on 2024-08-09 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_rename_role_user_role_type_alter_user_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_batch_printed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_kit_collected',
            field=models.BooleanField(default=False),
        ),
        # migrations.AlterField(
        #     model_name='user',
        #     name='password',
        #     field=models.CharField(max_length=128, verbose_name='password'),
        # ),
    ]
