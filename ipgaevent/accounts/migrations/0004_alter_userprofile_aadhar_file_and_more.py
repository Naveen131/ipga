# Generated by Django 5.0.6 on 2024-05-26 05:47

import ipgaevent.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_city_country_pincode_state_remove_address_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='aadhar_file',
            field=models.FileField(blank=True, null=True, storage=ipgaevent.storage_backends.PublicMediaStorage(), upload_to='aadhar_files/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gst_file',
            field=models.FileField(blank=True, null=True, storage=ipgaevent.storage_backends.PublicMediaStorage(), upload_to='gst_files/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='passport_file',
            field=models.FileField(blank=True, null=True, storage=ipgaevent.storage_backends.PublicMediaStorage(), upload_to='passport_files/'),
        ),
    ]
