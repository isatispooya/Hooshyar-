# Generated by Django 4.1.13 on 2024-07-02 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Visit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='kind',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='Visit.kindofcounseling'),
            preserve_default=False,
        ),
    ]
