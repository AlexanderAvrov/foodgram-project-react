# Generated by Django 2.2.16 on 2022-12-23 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_fix_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Ингредиент'),
        ),
    ]
