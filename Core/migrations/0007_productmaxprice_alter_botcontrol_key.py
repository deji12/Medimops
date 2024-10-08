# Generated by Django 5.1.1 on 2024-10-02 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0006_botcontrol_medimops_account_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductMaxPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='botcontrol',
            name='key',
            field=models.CharField(blank=True, default=b'sU8LxZOz7dLsVTcp7Bv1fzOsKyiwFbyvE7RwYBZAZlw=', max_length=255, null=True),
        ),
    ]
