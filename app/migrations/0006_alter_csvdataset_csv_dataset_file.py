# Generated by Django 4.1 on 2023-03-16 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_csvdataset_csv_dataset_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csvdataset',
            name='csv_dataset_file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
