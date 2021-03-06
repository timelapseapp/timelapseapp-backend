# Generated by Django 2.0.3 on 2018-03-23 19:06

import functools
import uuid

import django.db.models.deletion
from django.db import migrations, models

import timelapse_manager.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Camera",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, default="", max_length=255)),
                ("notes", models.TextField(blank=True, default="")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="CameraController",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, default="", max_length=255)),
                ("notes", models.TextField(blank=True, default="")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Day",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField(db_index=True)),
            ],
            options={"ordering": ("date",)},
        ),
        migrations.CreateModel(
            name="Frame",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("number", models.PositiveIntegerField()),
                ("realtime_timestamp", models.DateTimeField()),
            ],
            options={"ordering": ("movie_rendering", "number")},
        ),
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=255
                    ),
                ),
                (
                    "shot_at",
                    models.DateTimeField(
                        blank=True, db_index=True, default=None, null=True
                    ),
                ),
                (
                    "original",
                    models.ImageField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=255,
                        null=True,
                        storage=timelapse_manager.storage.dsn_setting_configured_storage(
                            "TIMELAPSE_STORAGE_DSN"
                        ),
                        upload_to="",
                    ),
                ),
                (
                    "original_md5",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=32
                    ),
                ),
                (
                    "scaled_at_160x120",
                    models.ImageField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=255,
                        null=True,
                        storage=timelapse_manager.storage.dsn_setting_configured_storage(
                            "TIMELAPSE_STORAGE_DSN"
                        ),
                        upload_to=functools.partial(
                            timelapse_manager.storage.upload_to_image,
                            *(),
                            **{"size": "160x120"}
                        ),
                    ),
                ),
                (
                    "scaled_at_160x120_md5",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=32
                    ),
                ),
                (
                    "scaled_at_320x240",
                    models.ImageField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=255,
                        null=True,
                        storage=timelapse_manager.storage.dsn_setting_configured_storage(
                            "TIMELAPSE_STORAGE_DSN"
                        ),
                        upload_to=functools.partial(
                            timelapse_manager.storage.upload_to_image,
                            *(),
                            **{"size": "320x240"}
                        ),
                    ),
                ),
                (
                    "scaled_at_320x240_md5",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=32
                    ),
                ),
                (
                    "scaled_at_640x480",
                    models.ImageField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=255,
                        null=True,
                        storage=timelapse_manager.storage.dsn_setting_configured_storage(
                            "TIMELAPSE_STORAGE_DSN"
                        ),
                        upload_to=functools.partial(
                            timelapse_manager.storage.upload_to_image,
                            *(),
                            **{"size": "640x480"}
                        ),
                    ),
                ),
                (
                    "scaled_at_640x480_md5",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=32
                    ),
                ),
            ],
            options={"ordering": ("shot_at",)},
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, default=None)),
                ("speed_factor", models.FloatField(default=4000.0)),
                (
                    "camera",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="movies",
                        to="timelapse_manager.Camera",
                    ),
                ),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="MovieRendering",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "size",
                    models.CharField(
                        choices=[
                            ("640x480", "640x480"),
                            ("320x240", "320x240"),
                            ("160x120", "160x120"),
                        ],
                        default="160x120",
                        max_length=32,
                    ),
                ),
                ("fps", models.FloatField(default=15.0)),
                ("format", models.CharField(default="mp4", max_length=255)),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=255,
                        null=True,
                        storage=timelapse_manager.storage.dsn_setting_configured_storage(
                            "TIMELAPSE_STORAGE_DSN"
                        ),
                        upload_to=timelapse_manager.storage.upload_to_movie_rendering,
                    ),
                ),
                (
                    "file_md5",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=32
                    ),
                ),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="renderings",
                        to="timelapse_manager.Movie",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Stream",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, default="", max_length=255)),
                ("notes", models.TextField(blank=True, default="")),
                ("location", models.TextField(blank=True, default="")),
                (
                    "auto_resize_original",
                    models.BooleanField(
                        default=False,
                        help_text="if enabled, every original image submitted through the imageintake will automatically be resized.",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                (
                    "stream",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tags",
                        to="timelapse_manager.Stream",
                    ),
                ),
            ],
            options={"ordering": ("start_at", "end_at")},
        ),
        migrations.CreateModel(
            name="TagInfo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, default="")),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="movie",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="movies", to="timelapse_manager.TagInfo"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="stream",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="images",
                to="timelapse_manager.Stream",
            ),
        ),
        migrations.AddField(
            model_name="frame",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="frames",
                to="timelapse_manager.Image",
            ),
        ),
        migrations.AddField(
            model_name="frame",
            name="movie_rendering",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="frames",
                to="timelapse_manager.MovieRendering",
            ),
        ),
        migrations.AddField(
            model_name="day",
            name="cover",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cover_for_days",
                to="timelapse_manager.Image",
            ),
        ),
        migrations.AddField(
            model_name="day",
            name="key_frames",
            field=models.ManyToManyField(
                blank=True,
                related_name="keyframe_for_days",
                to="timelapse_manager.Image",
            ),
        ),
        migrations.AddField(
            model_name="day",
            name="stream",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="days",
                to="timelapse_manager.Stream",
            ),
        ),
        migrations.AddField(
            model_name="camera",
            name="active_image_stream",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="timelapse_manager.Stream",
            ),
        ),
        migrations.AddField(
            model_name="camera",
            name="controller",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cameras",
                to="timelapse_manager.CameraController",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="image", unique_together={("stream", "shot_at")}
        ),
        migrations.AlterUniqueTogether(
            name="day", unique_together={("stream", "date")}
        ),
    ]
