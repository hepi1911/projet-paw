# Generated by Django 5.2 on 2025-05-05 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_booking_status_alter_companybooking_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='animal_type',
            field=models.CharField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('other', 'Other')], default='dog', max_length=10),
        ),
        migrations.AlterField(
            model_name='companybooking',
            name='status',
            field=models.CharField(choices=[('pending', 'En attente'), ('accepted', 'Acceptée'), ('refused', 'Refusée'), ('cancelled', 'Annulée'), ('paid', 'Payée')], default='pending', max_length=10),
        ),
    ]
