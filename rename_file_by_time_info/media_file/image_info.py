from __future__ import annotations

import datetime
import logging

from PIL import Image

from .media_file_info import DateAndTimeType, MediaFileInfo
from rename_file_by_time_info import general_file

if __debug__:
    import json


logger = logging.getLogger()


class ImageInfo(MediaFileInfo):
    @staticmethod
    def _exif_datetime_data_to_datetime_obj(
        naive_date_and_time: str,
        offset_time: str | None = None,
        subsecond_time: str | None = None,
    ) -> datetime.datetime | None:
        if isinstance(subsecond_time, str) and len(subsecond_time) > 6:
            raise ValueError(
                "Sub-second time cannot have resolution higher than microseconds: {}".format(
                    subsecond_time
                )
            )

        microsecond = (
            0
            if subsecond_time is None
            else int(subsecond_time) * (10 ** (6 - len(subsecond_time)))
        )
        time_zone = (
            datetime.timezone.utc
            if offset_time is None
            else datetime.timezone(
                offset=general_file.helper.offset_time_str_to_timedelta(
                    value=offset_time
                )
            )
        )
        try:
            return datetime.datetime.strptime(
                naive_date_and_time, "%Y:%m:%d %H:%M:%S"
            ).replace(microsecond=microsecond, tzinfo=time_zone)
        except ValueError:
            return None

    @classmethod
    def from_exiftool(cls, file_path: str) -> ImageInfo | None:
        exif_data = cls.get_exiftool_output(file_path=file_path)
        if __debug__:
            logger.debug("exif_data: %s", json.dumps(exif_data, indent=2))

        date_and_time_type = DateAndTimeType.AUTHENTIC
        date_and_time: datetime.datetime | None = None
        # Reference: https://exiftool.org/TagNames/EXIF.html
        for i, j, k in [
            ("DateTimeOriginal", "OffsetTimeOriginal", "SubSecTimeOriginal"),
            ("CreateDate", "OffsetTimeDigitized", "SubSecTimeDigitized"),
        ]:
            if i not in exif_data:
                continue
            date_and_time = cls._exif_datetime_data_to_datetime_obj(
                naive_date_and_time=exif_data[i],
                offset_time=exif_data.get(j, None),
                subsecond_time=(
                    None if k not in exif_data else str(exif_data[k])
                ),
            )
            break
        if date_and_time is None and "ModifyDate" in exif_data:
            date_and_time_type = DateAndTimeType.BEST
            date_and_time = cls._exif_datetime_data_to_datetime_obj(
                naive_date_and_time=exif_data["ModifyDate"],
                offset_time=exif_data.get("OffsetTime", None),
                subsecond_time=exif_data.get("SubSecTime", None),
            )

        if date_and_time is None:
            return None

        suspected_editing_software_keywords = [
            str(exif_data.get(i, ""))
            for i in [
                "Software",
                "ProcessingSoftware",
                "HistorySoftwareAgent",
                "CreatorTool",
            ]
        ]

        return cls(
            date_and_time_type=date_and_time_type,
            date_and_time=date_and_time,
            suspected_editing_software_keywords=suspected_editing_software_keywords,
        )

    @classmethod
    def from_pil(cls, file_path: str) -> ImageInfo | None:
        def get_exif_data(file_path: str) -> dict:
            with Image.open(file_path) as image:
                exif_data = image._getexif()
            if exif_data is None:
                return {}
            return exif_data

        exif_data = get_exif_data(file_path=file_path)
        if __debug__:
            keys_to_remove = [
                k for k, v in exif_data.items() if isinstance(v, bytes)
            ]
            for k in keys_to_remove:
                del exif_data[k]
            logger.debug("exif_data: %s", exif_data)

        date_and_time_type = DateAndTimeType.AUTHENTIC
        date_and_time: datetime.datetime | None = None
        for i, j, k in [(36867, 36881, 37521), (36868, 36882, 37522)]:
            if i not in exif_data:
                continue
            date_and_time = cls._exif_datetime_data_to_datetime_obj(
                naive_date_and_time=exif_data[i],
                offset_time=exif_data.get(j, None),
                subsecond_time=exif_data.get(k, None),
            )
            break
        if date_and_time is None and 306 in exif_data:
            date_and_time_type = DateAndTimeType.BEST
            date_and_time = cls._exif_datetime_data_to_datetime_obj(
                naive_date_and_time=exif_data[306],
                offset_time=exif_data.get(36880, None),
                subsecond_time=exif_data.get(37520, None),
            )

        if date_and_time is None:
            return None

        suspected_editing_software_keywords = [
            str(exif_data.get(i, "")) for i in [11, 305]
        ]

        return cls(
            date_and_time_type=date_and_time_type,
            date_and_time=date_and_time,
            suspected_editing_software_keywords=suspected_editing_software_keywords,
        )
