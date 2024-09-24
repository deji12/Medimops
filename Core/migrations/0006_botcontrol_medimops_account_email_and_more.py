# Generated by Django 5.1.1 on 2024-09-24 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0005_alter_botcontrol_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='botcontrol',
            name='medimops_account_email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='botcontrol',
            name='medimops_account_password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='botcontrol',
            name='key',
            field=models.CharField(blank=True, default=b'ddvzl4CHcPGCigmy8H77C-Py-L2tVdYDf4TGCQhGaC8=', max_length=255, null=True),
        ),
    ]
