# Generated by Django 4.1.3 on 2023-05-20 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_name_customer_address_customer_city_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-date_ordered',)},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'ordering': ('-date_added',)},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('-created_at',)},
        ),
    ]
