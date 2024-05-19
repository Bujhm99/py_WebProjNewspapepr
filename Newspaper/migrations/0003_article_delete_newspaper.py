# Generated by Django 4.1 on 2024-05-16 02:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Newspaper', '0002_alter_redactor_years_of_experience'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('content', models.TextField()),
                ('published_date', models.DateField()),
                ('publishers', models.ManyToManyField(related_name='articles', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to='Newspaper.topic')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.DeleteModel(
            name='Newspaper',
        ),
    ]
