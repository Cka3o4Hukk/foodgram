# Generated by Django 3.2.16 on 2024-11-23 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingredients',
            new_name='Ingredient',
        ),
        migrations.RenameModel(
            old_name='Tags',
            new_name='Tag',
        ),
    ]