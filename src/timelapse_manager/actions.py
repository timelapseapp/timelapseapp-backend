# -*- coding: utf-8 -*-
import collections
import datetime
import hashlib
import os

from django.core.files import File

import dateparser
import easy_thumbnails.files
import eliot

from timelapse_manager.models import Frame
from timelapse_manager.storage import timelapse_storage, upload_to_image

from . import models, utils


def discover_images_on_day(
    stream, stream_dir, day_name, sizes=None, storage=timelapse_storage
):
    models.Day.objects.get_or_create(date=dateparser.parse(day_name), stream=stream)
    sizes = sizes or ("original", "640x480", "320x240", "160x120")
    data = collections.defaultdict(dict)
    for size_name in storage.listdir(stream_dir)[0]:
        if size_name not in sizes:
            continue
        size_basedir = os.path.join(stream_dir, size_name)
        day_basedir = os.path.join(size_basedir, day_name)
        try:
            imagenames = storage.listdir(day_basedir)[1]
        except OSError:
            # the local filesystem storage fails when trying to list a directory
            # that does not exist. S3 storage just returns an empty list.
            # unfortunatly storage.exists() does not work on S3, as it returns
            # False for directories.
            continue
        for imagename in imagenames:
            if not imagename.lower().endswith(".jpg"):
                continue
            shot_at = utils.datetime_from_filename(imagename)
            imgdata = data[(str(stream.id), shot_at)]
            imagepath = os.path.join(day_basedir, imagename)

            imgdata["shot_at"] = shot_at
            imgdata["name"] = utils.original_filename_from_filename(imagename)

            if size_name == "original":
                imgdata["original"] = imagepath
                imgdata["original_md5"] = utils.md5sum_from_filename(imagename)
            else:
                imgdata["scaled_at_{}".format(size_name)] = imagepath
                imgdata[
                    "scaled_at_{}_md5".format(size_name)
                ] = utils.md5sum_from_filename(imagename)
            print(" -> discovered {}".format(imagepath))
    for imgdata in data.values():
        image, created = models.Image.objects.update_or_create(
            stream=stream, shot_at=imgdata.pop("shot_at"), defaults=imgdata
        )
        if created:
            print(" ==> created {}".format(imgdata["name"]))
        else:
            print(" ==> updated {}".format(imgdata["name"]))


def discover_images(
    storage=timelapse_storage, stream_dir="", stream=None, limit_days=None, sizes=None
):
    """
    directory relative to default storage root
    """
    sizes = sizes or ("original", "640x480", "320x240", "160x120")
    if stream is None:
        stream = models.Stream.objects.create(name=stream_dir)
    elif not isinstance(stream, models.Stream):
        stream = models.Stream.objects.get(id=stream)
    print(stream_dir)
    days = set()
    for size_name in storage.listdir(stream_dir)[0]:
        print(size_name)
        if size_name not in sizes:
            continue
        size_basedir = os.path.join(stream_dir, size_name)
        print(size_basedir)
        try:
            day_names = storage.listdir(size_basedir)[0]
        except OSError:
            # the local filesystem storage fails when trying to list a
            # directory that does not exist. S3 storage just returns an
            # empty list. Unfortunatly storage.exists() does not work on
            # S3, as it returns False for directories.
            day_names = []
        for day_name in day_names:
            print(day_name)
            if limit_days and not day_name in limit_days:
                continue
            days.add(day_name)
    for day_name in days:
        print(day_name)
        discover_images_on_day(
            stream=stream,
            day_name=day_name,
            sizes=sizes,
            storage=storage,
            stream_dir=stream_dir,
        )


def create_or_update_images_from_urls(urls):
    """
    Takes a list of urls and creates or updates matching Images in the database.
    This function is smart about only making one db query if multiple urls of
    the same image are provided.
    """
    data = collections.defaultdict(dict)
    for url in urls:
        img = utils.image_url_to_structured_data(url)
        img_data = data[(img["camera_name"], img["shot_at"])]
        img_data["camera_name"] = img["camera_name"]
        img_data["shot_at"] = img["shot_at"]
        img_data["name"] = img["name"]
        if img["size_name"] == "original":
            img_data["original"] = img["path"]
            img_data["original_md5"] = img["md5"]
        else:
            img_data["scaled_at_{}".format(img["size_name"])] = img["path"]
            img_data["scaled_at_{}_md5".format(img["size_name"])] = img["md5"]
    cameras = {}
    images = []
    days = set()
    for img_data in data.values():
        camera_name = img_data.pop("camera_name")
        shot_at = img_data.pop("shot_at")
        days.add((camera_name, shot_at.date()))
        if camera_name not in cameras:
            cameras[camera_name] = models.Camera.objects.get(name=camera_name)
        image, created = models.Image.objects.update_or_create(
            camera=cameras[camera_name], shot_at=shot_at, defaults=img_data
        )
        images.append(image)
        if created:
            print(
                " ==> created {} {}".format(
                    ", ".join(img_data.keys()), img_data["name"]
                )
            )
        else:
            print(
                " ==> updated {} {}".format(
                    ", ".join(img_data.keys()), img_data["name"]
                )
            )
        if cameras[camera_name].auto_resize_original:
            from .tasks import create_thumbnails_for_image

            create_thumbnails_for_image.delay(image_id=str(image.id))
    for camera_name, date in days:
        models.Day.objects.get_or_create(camera=cameras[camera_name], date=date)
    return images


def create_or_update_image_from_url(url):
    """
    takes an s3 url or relative url:
    - detects the size and other meta data
    - creates or updates the Image model with the new file
    """
    img = utils.image_url_to_structured_data(url)
    camera_name = img["camera_name"]
    filename = img["filename"]
    size_name = img["size_name"]
    path = img["path"]
    shot_at = img["shot_at"]
    camera = models.Camera.objects.get(name=camera_name)

    defaults = dict(name=utils.original_filename_from_filename(filename))

    if size_name == "original":
        defaults["original"] = path
        defaults["original_md5"] = img["md5"]
    else:
        defaults["scaled_at_{}".format(size_name)] = path
        defaults["scaled_at_{}_md5".format(img["size_name"])] = img["md5"]

    image, created = models.Image.objects.update_or_create(
        camera=camera, shot_at=shot_at, defaults=defaults
    )
    if created:
        print(" ==> created {} {}".format(size_name, filename))
    else:
        print(" ==> updated {} {}".format(size_name, filename))
    return image, created


def create_thumbnail(image, size):
    total = 2
    with eliot.start_action(
        action_type="timelapse:image:create_thumbnail", size=size, image=str(image.pk)
    ) as action:
        if not image.original:
            raise Exception("missing original")
        thumbnailer = easy_thumbnails.files.get_thumbnailer(image.original)
        size_tuple = tuple([int(sz) for sz in size.split("x")])
        options = {"size": size_tuple, "upscale": False}
        thumb = thumbnailer.generate_thumbnail(options)
        eliot.Message.log(
            message_type="thumbnail-generated", progress={"done": 1, "total": total}
        )
        content_file = thumb.file
        content_file.name = "afile.jpg"
        content_file.seek(0)
        md5sum = hashlib.md5(content_file.read()).hexdigest()
        eliot.Message.log(
            message_type="md5-generated", progress={"done": 2, "total": total}
        )
        content_file.seek(0)
        setattr(image, "scaled_at_{}".format(size), content_file)
        setattr(image, "scaled_at_{}_md5".format(size), md5sum)


def create_thumbnails(image, force=False):
    total = len(image.sizes)
    with eliot.start_action(
        action_type="timelapse:image:create_thumbnails", image=str(image.pk)
    ) as action:
        for idx, size in enumerate(image.sizes, start=1):
            if force or not getattr(image, "scaled_at_{}".format(size)):
                create_thumbnail(image, size)
                eliot.Message.log(
                    message_type="progress",
                    size=size,
                    progress={"done": idx, "total": total},
                )
            else:
                eliot.Message.log(
                    message_type="progress",
                    size=size,
                    alread_exists=True,
                    progress={"done": idx, "total": total},
                )


def set_keyframes_for_day(day):
    day.cover = models.Image.objects.pick_closest(
        stream=day.stream,
        shot_at=datetime.datetime.combine(day.date, datetime.time(16, 0)),
        max_difference=datetime.timedelta(hours=2),
    )
    day.save()
    keyframes = [
        datetime.time(6, 0),
        datetime.time(9, 0),
        datetime.time(12, 30),
        datetime.time(15, 0),
        datetime.time(18, 0),
    ]
    images = []
    for keyframe in keyframes:
        image = models.Image.objects.pick_closest(
            stream=day.stream,
            shot_at=datetime.datetime.combine(day.date, keyframe),
            max_difference=datetime.timedelta(hours=1),
        )
        if image:
            images.append(image)
    day.key_frames.set(images)


def image_count_by_type():
    qs = models.Image.objects.all()
    data = {
        "160x120": qs.exclude(scaled_at_160x120="").count(),
        "320x240": qs.exclude(scaled_at_320x240="").count(),
        "640x480": qs.exclude(scaled_at_640x480="").count(),
        "original": qs.exclude(original="").count(),
    }
    return "  ".join(["{}: {}".format(key, value) for key, value in data.items()])


def create_frames_for_movie_rendering(movie_rendering):
    movie_rendering.frames.all().delete()
    number = 0
    for timestamp in movie_rendering.wanted_frame_timestamps:
        frame = Frame(
            movie_rendering=movie_rendering, number=number, realtime_timestamp=timestamp
        )
        frame.pick_image()
        frame.save()
        number += 1


def render_movie(movie_rendering):
    from . import moviepy

    if not movie_rendering.frames.all().exists():
        movie_rendering.create_frames()
    moviepath = moviepy.render_video(
        queryset=movie_rendering.frames.all().select_related("image"),
        size=movie_rendering.size,
        format=movie_rendering.format,
        fps=movie_rendering.fps,
        duration=movie_rendering.movie.movie_duration.total_seconds(),
    )
    with open(moviepath, "rb") as f:
        md5sum = hashlib.md5(f.read()).hexdigest()
        f.seek(0)
        movie_rendering.file_md5 = md5sum
        django_file = File(f)
        movie_rendering.file = django_file
        movie_rendering.save()


def delete_thumbnails(qs):
    for image in qs.iterator():
        print("handling {}".format(image.name))
        for size in image.sizes:
            size_field_name = "scaled_at_{}".format(size)
            size_field_md5_name = "scaled_at_{}_md5".format(size)
            image_size = getattr(image, size_field_name)
            if image_size:
                print("  -> deleting {}".format(image_size.url))
                image_size.delete()
                setattr(image, size_field_md5_name, "")
        image.save()


def set_image_name_based_on_original_filename(qs):
    for image in qs:
        if not image.original:
            print("skipping {}. missing original".format(image))
        name = utils.image_url_to_structured_data(image.original.url)["name"]
        if name != image.name:
            print("changing {} to {}".format(image.name, name))
            image.name = name
            image.save()
        else:
            print("skipping {}. name already correct")


def import_images(stream, storage, path):
    with eliot.start_action(action_type="timelapse:images:import") as action:
        dirs, file_names = storage.listdir(path)
        total = len(file_names)
        # FIXME: file_name should be combination of path and dir
        for idx, file_name in enumerate(file_names):
            if not file_name.lower().endswith(".jpg"):
                continue
            import_image(stream, storage, file_name)
            eliot.Message.log(progress={"done": idx, "total": total})


def import_image(stream, storage, path):
    with eliot.start_action(action_type="timelapse:image:import") as action:
        total = 5
        eliot.Message.log(source=path)
        # image_path = '/'.join([path, path]).lstrip('/')
        with storage.open(path) as image_file:
            eliot.Message.log(
                message_type="file-opened", progress={"done": 1, "total": total}
            )
            shot_at = utils.datetime_from_exif(image_file)
            eliot.Message.log(
                message_type="date-extracted", progress={"done": 2, "total": total}
            )
            md5sum = utils.md5sum_from_fileobj(image_file)
            eliot.Message.log(
                message_type="md5-generated", progress={"done": 3, "total": total}
            )
            print(shot_at, end="  ")
            image, created = models.Image.objects.update_or_create(
                stream=stream,
                shot_at=shot_at,
                defaults=dict(
                    name=path, original_md5=md5sum  # FIXME: only filename from path!
                ),
            )
            eliot.Message.log(
                message_type="model-saved",
                created=created,
                progress={"done": 4, "total": total},
            )
            upload_to_name = upload_to_image(image, size="original")
            image.original.save(upload_to_name, image_file)
            eliot.Message.log(
                message_type="image-saved",
                destination=upload_to_name,
                progress={"done": 5, "total": total},
            )
