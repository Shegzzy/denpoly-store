# Generated by Django 4.1.3 on 2023-06-09 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_customer_options_alter_order_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='colors',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
