# Generated by Django 3.2.16 on 2024-11-26 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0003_auto_20241125_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=1, upload_to='foodgram/recipes/images/'),
            preserve_default=False,
        ),
    ]