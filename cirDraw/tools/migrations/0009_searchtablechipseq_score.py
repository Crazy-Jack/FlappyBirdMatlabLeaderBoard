# Generated by Django 3.2 on 2021-07-30 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0008_auto_20210730_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchtablechipseq',
            name='score',
            field=models.FloatField(db_column='score', null=True),
        ),
    ]
