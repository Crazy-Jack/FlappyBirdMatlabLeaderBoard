# Generated by Django 3.2.25 on 2024-04-24 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('md5', models.CharField(db_column='md5', max_length=255)),
                ('upload_file_location', models.CharField(db_column='upload_file_location', max_length=255)),
                ('submission_time', models.DateTimeField(auto_now=True, db_column='submission_time')),
                ('youtube_url', models.CharField(db_column='youtube_url', max_length=255)),
                ('category', models.IntegerField(db_column='category', default='')),
                ('best_score', models.IntegerField(db_column='best_score', default='')),
                ('andrewid', models.CharField(db_column='andrewid', max_length=255)),
                ('username', models.CharField(db_column='username', max_length=255)),
                ('train_time', models.FloatField(db_column='train_time', null=True)),
                ('train_episode', models.IntegerField(db_column='train_episode', default='')),
                ('train_deaths', models.IntegerField(db_column='train_deaths', default='')),
                ('num_nn', models.IntegerField(db_column='num_nn', default='')),
            ],
            options={
                'db_table': 'SubmissionTable',
            },
        ),
    ]