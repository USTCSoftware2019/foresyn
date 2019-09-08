# Generated by Django 2.2.3 on 2019-09-08 04:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareAuthorization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public', models.BooleanField()),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.RemoveField(
            model_name='metaboliteshare',
            name='public',
        ),
        migrations.RemoveField(
            model_name='modelshare',
            name='public',
        ),
        migrations.RemoveField(
            model_name='reactionshare',
            name='public',
        ),
        migrations.AlterField(
            model_name='metaboliteshare',
            name='metabolite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraMetabolite'),
        ),
        migrations.AlterField(
            model_name='modelshare',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraModel'),
        ),
        migrations.AlterField(
            model_name='reactionshare',
            name='reaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cobra_wrapper.CobraReaction'),
        ),
        migrations.AddField(
            model_name='metaboliteshare',
            name='auth',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='share.ShareAuthorization'),
        ),
        migrations.AddField(
            model_name='modelshare',
            name='auth',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='share.ShareAuthorization'),
        ),
        migrations.AddField(
            model_name='reactionshare',
            name='auth',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='share.ShareAuthorization'),
        ),
    ]
