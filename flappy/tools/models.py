# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models


class SubmissionTable(models.Model):
    md5 = models.CharField(max_length=255, db_column='md5')
    upload_file_location = models.CharField(max_length=255, db_column='upload_file_location')
    submission_time = models.DateTimeField(auto_now=True, db_column='submission_time')
    youtube_url = models.CharField(max_length=255, db_column='youtube_url')
    
    category = models.IntegerField(db_column='category', default="")
    best_score = models.IntegerField(db_column='best_score', default="")
    andrewid = models.CharField(max_length=255, db_column='andrewid')
    username = models.CharField(max_length=255, db_column='username')
    
    train_time = models.FloatField(null=True, db_column='train_time')
    train_episode = models.IntegerField(db_column='train_episode', default="")
    train_deaths =  models.IntegerField(db_column='train_deaths', default="")

    num_nn  =  models.IntegerField(db_column='num_nn', default="")
    class Meta:
        db_table = 'SubmissionTable'


