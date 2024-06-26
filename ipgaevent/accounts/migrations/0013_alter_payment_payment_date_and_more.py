# Generated by Django 5.0.6 on 2024-05-28 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_payment_amount_alter_payment_amount_paid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_mode',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Card', 'Card'), ('Net Banking', 'Net Banking'), ('UPI', 'UPI')], default='Net Banking', max_length=255),
        ),
    ]
