# Generated by Django 2.2 on 2020-01-25 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_auto_20200125_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product', to='shop.Product'),
        ),
    ]
