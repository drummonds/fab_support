# Generated by Django 2.0.2 on 2018-02-14 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MyData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=255, verbose_name="A Name"),
                ),
                ("number", models.IntegerField(verbose_name="A Number")),
            ],
        )
    ]
