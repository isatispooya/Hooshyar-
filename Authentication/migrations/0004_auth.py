# Generated by Django 4.1.13 on 2024-06-26 05:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0003_rename_phone_authentication_mobile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=200)),
                ('national_code', models.IntegerField()),
                ('mobile', models.IntegerField()),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('password', models.CharField(max_length=800)),
                ('date_birth', models.DateField(blank=True, null=True)),
                ('date_last_act', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
