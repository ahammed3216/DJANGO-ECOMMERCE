# Generated by Django 2.1.5 on 2020-09-12 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_auto_20200912_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biriyani',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='biriyani',
            name='remarks',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('SW', 'SPORTWEAR'), ('OW', 'OUTWEAR'), ('S', 'SHIRT')], max_length=2),
        ),
        migrations.AlterField(
            model_name='item',
            name='labels',
            field=models.CharField(choices=[('D', 'danger'), ('P', 'primary'), ('S', 'secondary')], max_length=1),
        ),
    ]