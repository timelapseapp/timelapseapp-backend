# Generated by Django 2.0.3 on 2018-03-20 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timelapse_manager', '0011_camera_auto_resize_original'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='camera',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='days', to='timelapse_manager.Camera'),
        ),
        migrations.AlterField(
            model_name='day',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cover_for_days', to='timelapse_manager.Image'),
        ),
        migrations.AlterField(
            model_name='frame',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='frames', to='timelapse_manager.Image'),
        ),
        migrations.AlterField(
            model_name='frame',
            name='movie_rendering',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='frames', to='timelapse_manager.MovieRendering'),
        ),
        migrations.AlterField(
            model_name='image',
            name='camera',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='images', to='timelapse_manager.Camera'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='camera',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movies', to='timelapse_manager.Camera'),
        ),
        migrations.AlterField(
            model_name='movierendering',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='renderings', to='timelapse_manager.Movie'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='camera',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='timelapse_manager.Camera'),
        ),
    ]
