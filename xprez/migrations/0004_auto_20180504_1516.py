# Generated by Django 2.0.5 on 2018-05-04 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xprez', '0003_auto_20180117_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_type',
            field=models.CharField(choices=[('youtube', 'YouTube'), ('vimeo', 'Vimeo')], max_length=50),
        ),
    ]