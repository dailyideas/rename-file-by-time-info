import datetime
import logging
import os

from .image_info import ImageInfo
from .media_file_info import DateAndTimeType
from .media_file_name_formatter import MediaFileNameFormatter
from .video_and_audio_info import VideoAndAudioInfo
from rename_file_by_time_info import general_file


logger = logging.getLogger()


def get_renamed_image_file(
    file_path: str,
    naming_format: str,
    forced_offset_time: str | None = None,
    forced_date: datetime.date | None = None,
    exif_offset_time: str | None = None,
    use_exiftool: bool = True,
) -> str:
    time_zone = (
        datetime.timezone.utc
        if forced_offset_time is None
        else datetime.timezone(
            offset=general_file.helper.offset_time_str_to_timedelta(
                value=forced_offset_time
            )
        )
    )

    image_info: ImageInfo | None = None
    if use_exiftool:
        image_info = ImageInfo.from_exiftool(file_path=file_path)
    if image_info is None:
        image_info = ImageInfo.from_pil(file_path=file_path)
    if image_info is None:
        image_info = ImageInfo.from_file_status(file_path=file_path)
    if exif_offset_time is not None:
        exif_time_zone = datetime.timezone(
            offset=general_file.helper.offset_time_str_to_timedelta(
                value=exif_offset_time
            )
        )
        image_info.date_and_time = image_info.date_and_time.replace(
            tzinfo=exif_time_zone
        )
    if (
        forced_date is None
        or image_info.date_and_time_type == DateAndTimeType.AUTHENTIC
    ):
        date_and_time = image_info.date_and_time
        date_and_time_type = image_info.date_and_time_type
    else:
        date_and_time = datetime.datetime.combine(
            date=forced_date, time=datetime.time.min, tzinfo=time_zone
        )
        date_and_time_type = DateAndTimeType.CURATED
    if forced_offset_time is not None:
        date_and_time = date_and_time.astimezone(tz=time_zone)
    media_file_name_formatter = MediaFileNameFormatter(
        year=date_and_time.year,
        month=date_and_time.month,
        day=date_and_time.day,
        hour=date_and_time.hour,
        minute=date_and_time.minute,
        second=date_and_time.second,
        millisecond=date_and_time.microsecond // 1000,
        timezone=date_and_time.tzinfo,
        date_and_time_type=date_and_time_type,
        edit_type=image_info.edit_type,
    )
    _, file_extension = general_file.helper.get_file_name_prefix_and_extension(
        file_path
    )
    return media_file_name_formatter.get_formatted_filename(
        naming_format="{}.{}".format(naming_format, file_extension)
    )


def get_renamed_video_or_audio_file(
    file_path: str,
    naming_format: str,
    forced_offset_time: str | None = None,
    forced_date: datetime.date | None = None,
    exif_offset_time: str | None = None,
) -> str:
    time_zone = (
        datetime.timezone.utc
        if forced_offset_time is None
        else datetime.timezone(
            offset=general_file.helper.offset_time_str_to_timedelta(
                value=forced_offset_time
            )
        )
    )

    video_and_audio_info = VideoAndAudioInfo.from_exiftool(file_path=file_path)
    if video_and_audio_info is None:
        video_and_audio_info = VideoAndAudioInfo.from_file_status(
            file_path=file_path
        )
    if exif_offset_time is not None:
        exif_time_zone = datetime.timezone(
            offset=general_file.helper.offset_time_str_to_timedelta(
                value=exif_offset_time
            )
        )
        video_and_audio_info.date_and_time = (
            video_and_audio_info.date_and_time.replace(tzinfo=exif_time_zone)
        )
    if (
        forced_date is None
        or video_and_audio_info.date_and_time_type == DateAndTimeType.AUTHENTIC
    ):
        date_and_time = video_and_audio_info.date_and_time
        date_and_time_type = video_and_audio_info.date_and_time_type
    else:
        date_and_time = datetime.datetime.combine(
            date=forced_date, time=datetime.time.min, tzinfo=time_zone
        )
        date_and_time_type = DateAndTimeType.CURATED
    if forced_offset_time is not None:
        date_and_time = date_and_time.astimezone(tz=time_zone)
    media_file_name_formatter = MediaFileNameFormatter(
        year=date_and_time.year,
        month=date_and_time.month,
        day=date_and_time.day,
        hour=date_and_time.hour,
        minute=date_and_time.minute,
        second=date_and_time.second,
        millisecond=0,
        timezone=date_and_time.tzinfo,
        date_and_time_type=date_and_time_type,
        edit_type=video_and_audio_info.edit_type,
    )
    _, file_extension = general_file.helper.get_file_name_prefix_and_extension(
        file_path
    )
    return media_file_name_formatter.get_formatted_filename(
        naming_format="{}.{}".format(naming_format, file_extension)
    )


def rename(
    file_path: str,
    naming_format: str,
    forced_offset_time: str | None = None,
    forced_date: datetime.date | None = None,
    exif_offset_time: str | None = None,
    use_exiftool_on_images: bool = True,
    image_file_extensions: list[str] | None = None,
    video_and_audio_file_extensions: list[str] | None = None,
    skip_if_file_name_matches_naming_format: bool = False,
) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")
    if image_file_extensions is None:
        image_file_extensions = []
    if video_and_audio_file_extensions is None:
        video_and_audio_file_extensions = []
    image_file_extensions = [i.lower() for i in image_file_extensions]
    video_and_audio_file_extensions = [
        i.lower() for i in video_and_audio_file_extensions
    ]

    file_name = os.path.basename(file_path)
    file_name_prefix, file_extension = (
        general_file.helper.get_file_name_prefix_and_extension(
            file_name_or_path=file_name
        )
    )
    if (
        skip_if_file_name_matches_naming_format
        and general_file.helper.file_name_matches_file_format(
            file_name_formatter=MediaFileNameFormatter,
            file_name=file_name_prefix,
            naming_format=naming_format,
        )
    ):
        logger.info("Skip files with matching naming format: %s", file_path)
        return

    file_extension_lowercase = file_extension.lower()
    if file_extension_lowercase in image_file_extensions:
        new_file_name = get_renamed_image_file(
            file_path=file_path,
            naming_format=naming_format,
            forced_offset_time=forced_offset_time,
            forced_date=forced_date,
            exif_offset_time=exif_offset_time,
            use_exiftool=use_exiftool_on_images,
        )
    elif file_extension_lowercase in video_and_audio_file_extensions:
        new_file_name = get_renamed_video_or_audio_file(
            file_path=file_path,
            naming_format=naming_format,
            forced_offset_time=forced_offset_time,
            forced_date=forced_date,
            exif_offset_time=exif_offset_time,
        )
    else:
        logger.info("Not a supported media file: %s", file_name)
        return
    file_directory = os.path.dirname(file_path)
    new_file_path = os.path.join(file_directory, new_file_name)
    if os.path.normpath(file_path) == os.path.normpath(new_file_path):
        logger.info("File unchanged: %s", file_name)
        return
    if os.path.isfile(new_file_path):
        new_file_path = (
            general_file.helper.modify_file_path_until_no_duplication_exists(
                file_path=new_file_path, replaceable_file_path=file_path
            )
        )
    os.rename(file_path, new_file_path)
    logger.info("%s -> %s", file_name, os.path.basename(new_file_path))
