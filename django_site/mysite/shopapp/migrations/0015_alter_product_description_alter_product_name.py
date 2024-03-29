# Generated by Django 4.2.1 on 2023-10-17 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0014_alter_productimage_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
