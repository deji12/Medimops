# Generated by Django 5.1.1 on 2024-09-25 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0006_botcontrol_medimops_account_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='botcontrol',
            name='card_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='botcontrol',
            name='key',
            field=models.CharField(blank=True, default=b'Dpxkuq8BgpsT__POURcKSXMtourJino0gfgkgb1NXxQ=', max_length=255, null=True),
        ),
    ]
