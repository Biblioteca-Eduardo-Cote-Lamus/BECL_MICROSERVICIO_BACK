# Generated by Django 4.2 on 2023-09-18 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rol_Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=150)),
                ('facultad', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=150)),
                ('usuario', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=300)),
                ('rol', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rol_usuario', to='BECL_Login.rol_usuario')),
            ],
        ),
    ]
