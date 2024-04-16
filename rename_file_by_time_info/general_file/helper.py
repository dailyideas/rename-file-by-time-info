import datetime
import logging
import os
import re
from typing import Type

from .file_name_formatter import FileNameFormatter


logger = logging.getLogger()


def get_file_name_prefix_and_extension(
    file_name_or_path: str,
) -> tuple[str, str]:
    file_name = os.path.basename(file_name_or_path)
    extension_dot_index = file_name.rfind(".")
    if extension_dot_index == -1:
        return file_name, ""
    else:
        return (
            file_name[:extension_dot_index],
            file_name[extension_dot_index + 1 :],
        )


def offset_time_str_to_timedelta(value: str) -> datetime.timedelta:
    if value[0] not in ["+", "-"]:
        raise ValueError("The first character must be either +/-")
    s = value[0]
    if ":" in value:
        h, m = int(value[1:3]), int(value[4:6])
    else:
        h, m = int(value[1:3]), int(value[3:5])
    return (
        datetime.timedelta(hours=h, minutes=m)
        if s == "+"
        else datetime.timedelta(hours=-h, minutes=-m)
    )


def modify_file_path_until_no_duplication_exists(
    file_path: str,
    lower_limit: int = 1,
    upper_limit: int = 10000,
    replaceable_file_path: str = "",
) -> str:
    file_directory = os.path.dirname(file_path)
    file_name_prefix, file_extension = get_file_name_prefix_and_extension(
        file_name_or_path=file_path
    )
    for i in range(lower_limit, upper_limit):
        i_str = str(i).zfill(4)
        new_file_name = f"{file_name_prefix}_{i_str}.{file_extension}"
        new_file_path = os.path.join(file_directory, new_file_name)
        if (
            not os.path.isfile(new_file_path)
            or new_file_path == replaceable_file_path
        ):
            return new_file_path
    raise ValueError(
        "Could not find a unique file name for file: {}".format(file_path)
    )


def file_name_matches_file_format(
    file_name_formatter: Type[FileNameFormatter],
    file_name: str,
    naming_format: str,
) -> bool:
    regex = file_name_formatter.get_regex_of_naming_format(
        naming_format=naming_format
    )
    regex = r"^" + regex + r"(_\d{4})?$"
    return re.match(regex, file_name) is not None


def rename(
    file_path: str,
    naming_format: str,
    forced_offset_time: str | None = None,
    forced_date: datetime.date | None = None,
    skip_if_file_name_matches_naming_format: bool = False,
) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError("No such file: {}".format(file_path))

    file_name = os.path.basename(file_path)
    file_name_prefix, file_extension = get_file_name_prefix_and_extension(
        file_name_or_path=file_path
    )
    if (
        skip_if_file_name_matches_naming_format
        and file_name_matches_file_format(
            file_name_formatter=FileNameFormatter,
            file_name=file_name_prefix,
            naming_format=naming_format,
        )
    ):
        logger.info("Skip files with matching naming format: %s", file_path)
        return

    time_zone = (
        datetime.timezone.utc
        if forced_offset_time is None
        else datetime.timezone(
            offset=offset_time_str_to_timedelta(value=forced_offset_time)
        )
    )
    date_and_time: datetime.datetime
    if forced_date is None:
        date_and_time = datetime.datetime.fromtimestamp(
            os.stat(file_path).st_mtime, tz=time_zone
        )
    else:
        date_and_time = datetime.datetime.combine(
            date=forced_date, time=datetime.time.min, tzinfo=time_zone
        )

    file_name_formatter = FileNameFormatter(
        year=date_and_time.year,
        month=date_and_time.month,
        day=date_and_time.day,
        hour=date_and_time.hour,
        minute=date_and_time.minute,
        second=date_and_time.second,
        millisecond=0,
        timezone=date_and_time.tzinfo,
    )
    new_file_name = file_name_formatter.get_formatted_filename(
        naming_format="{}.{}".format(naming_format, file_extension)
    )
    file_directory = os.path.dirname(file_path)
    new_file_path = os.path.join(file_directory, new_file_name)
    if os.path.normpath(file_path) == os.path.normpath(new_file_path):
        logger.info("File unchanged: %s", file_name)
        return
    if os.path.isfile(new_file_path):
        new_file_path = modify_file_path_until_no_duplication_exists(
            file_path=new_file_path,
            replaceable_file_path=file_path,
        )
    os.rename(file_path, new_file_path)
    logger.info("%s -> %s", file_name, os.path.basename(new_file_path))
