# Generated by Django 4.2 on 2023-04-20 22:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('BECL_Login', '0004_merge_20230413_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='Events_P',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=150)),
                ('fecha', models.CharField(max_length=50)),
                ('hora_inicio', models.CharField(max_length=20)),
                ('hora_final', models.CharField(max_length=20)),
                ('asistente', models.IntegerField()),
                ('codigo_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_event', to='BECL_Login.usuarios')),
            ],
        ),
        migrations.CreateModel(
            name='Events_DB',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=150)),
                ('fecha', models.CharField(max_length=50)),
                ('hora_inicio', models.CharField(max_length=20)),
                ('hora_final', models.CharField(max_length=20)),
                ('asistente', models.IntegerField()),
                ('codigo_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_db', to='BECL_Login.usuarios')),
            ],
        ),
    ]
