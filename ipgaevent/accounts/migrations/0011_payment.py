# Generated by Django 5.0.6 on 2024-05-28 05:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_address_address_type_address_is_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=20)),
                ('payment_mode', models.CharField(choices=[('Cash', 'Cash'), ('Card', 'Card'), ('Net Banking', 'Net Banking'), ('UPI', 'UPI')], max_length=255)),
                ('payment_date', models.DateTimeField()),
                ('reference_id', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed'), ('Paid', 'Paid'), ('Partial', 'Partial')], max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]