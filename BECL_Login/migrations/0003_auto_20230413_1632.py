# Generated by Django 4.2 on 2023-04-13 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BECL_Login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=150)),
                ('facultad', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=150)),
                ('usuario', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=300)),
            ],
        ),
    ]
