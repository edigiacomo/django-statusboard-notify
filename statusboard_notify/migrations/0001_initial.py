# Generated by Django 2.2 on 2021-05-20 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('statusboard', '0022_auto_20201204_0856'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('services', models.ManyToManyField(to='statusboard.Service', verbose_name='services')),
            ],
            options={
                'verbose_name': 'recipient',
                'verbose_name_plural': 'recipients',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_status', models.IntegerField(blank=True, choices=[(0, 'Operational'), (1, 'Performance issues'), (2, 'Partial outage'), (3, 'Major outage')], null=True)),
                ('to_status', models.IntegerField(choices=[(0, 'Operational'), (1, 'Performance issues'), (2, 'Partial outage'), (3, 'Major outage')])),
                ('service', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='statusboard.Service')),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
            },
        ),
    ]
