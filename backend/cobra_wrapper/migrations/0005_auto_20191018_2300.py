# Generated by Django 2.2.6 on 2019-10-18 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cobra_wrapper', '0004_auto_20191017_2159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cobramodelchange',
            name='new_info',
        ),
        migrations.RemoveField(
            model_name='cobramodelchange',
            name='pre_info',
        ),
        migrations.AddField(
            model_name='cobramodel',
            name='desc',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='cobramodelchange',
            name='reaction_info',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cobramodelchange',
            name='change_type',
            field=models.CharField(choices=[('add_reaction', 'add_reaction'), ('del_reaction', 'del_reaction')], max_length=50),
        ),
    ]
