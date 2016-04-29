# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 10:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='bigparty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=128)),
                ('client_name', models.CharField(max_length=128)),
                ('client_idcard', models.CharField(max_length=128)),
                ('bank', models.CharField(max_length=128)),
                ('bank_card', models.CharField(max_length=128)),
                ('money', models.CharField(max_length=128)),
                ('startdate', models.CharField(max_length=32)),
                ('enddate', models.CharField(max_length=32)),
                ('status', models.IntegerField()),
                ('renewal_father_id', models.IntegerField()),
                ('renewal_son_id', models.IntegerField()),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='cycle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('cycletype', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('address', models.CharField(max_length=128)),
                ('tel', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='loginfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=1024)),
                ('time', models.CharField(max_length=128)),
                ('thisuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='manager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('tel', models.CharField(max_length=32)),
                ('number', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('thisbigparty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.bigparty')),
            ],
        ),
        migrations.CreateModel(
            name='product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('rate', models.CharField(max_length=16)),
                ('closedtype', models.CharField(max_length=16)),
                ('closedperiod', models.IntegerField()),
                ('repaycycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.cycle')),
            ],
        ),
        migrations.CreateModel(
            name='repayitem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repaydate', models.CharField(max_length=32)),
                ('repaymoney', models.CharField(max_length=128)),
                ('repaytype', models.IntegerField()),
                ('status', models.IntegerField()),
                ('thiscontract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.contract')),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('username', models.CharField(max_length=128)),
                ('position', models.CharField(max_length=128)),
                ('jurisdiction', models.IntegerField()),
                ('thisuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='manager',
            name='thisparty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.party'),
        ),
        migrations.AddField(
            model_name='contract',
            name='thismanager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.manager'),
        ),
        migrations.AddField(
            model_name='contract',
            name='thisproduct',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.product'),
        ),
        migrations.AddField(
            model_name='bigparty',
            name='thisfield',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.field'),
        ),
    ]
