# Generated by Django 4.1.13 on 2024-07-02 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Visit', '0004_visit_kind'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kindofcounseling',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
