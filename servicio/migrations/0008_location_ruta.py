# Generated by Django 5.1.3 on 2025-03-19 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicio', '0007_registroventa_deuda_anterior'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='ruta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locations', to='servicio.divisionempleado'),
        ),
    ]
