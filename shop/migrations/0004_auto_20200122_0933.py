# Generated by Django 2.2 on 2020-01-22 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20200121_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.FileField(upload_to='static/images/'),
        ),
    ]
