from __future__ import annotations

import dataclasses
import datetime
import logging

from .media_file_info import DateAndTimeType, MediaFileInfo
from rename_file_by_time_info import general_file

if __debug__:
    import json


logger = logging.getLogger()


@dataclasses.dataclass
class VideoAndAudioInfo(MediaFileInfo):
    @classmethod
    def from_exiftool(cls, file_path: str) -> VideoAndAudioInfo | None:
        def _exif_datetime_data_to_datetime_obj(
            naive_date_and_time: str,
            time_zone: datetime.timezone | None = None,
        ) -> datetime.datetime | None:
            if time_zone is None:
                time_zone = datetime.timezone.utc
            try:
                return datetime.datetime.strptime(
                    naive_date_and_time, "%Y:%m:%d %H:%M:%S"
                ).replace(tzinfo=time_zone)
            except ValueError:
                return None

        exif_data = cls.get_exiftool_output(file_path=file_path)
        if __debug__:
            logger.debug("exif_data: %s", json.dumps(exif_data, indent=2))

        offset_time: str | None = None
        for i in ["OffsetTimeOriginal", "OffsetTimeDigitized", "OffsetTime"]:
            if exif_data.get(i, None) is None:
                continue
            offset_time = exif_data[i]
            break
        time_zone = (
            datetime.timezone.utc
            if offset_time is None
            else datetime.timezone(
                offset=general_file.helper.offset_time_str_to_timedelta(
                    value=offset_time
                )
            )
        )

        date_and_time_type = DateAndTimeType.AUTHENTIC
        date_and_time: datetime.datetime | None = None
        for keyword in [
            "DateTimeOriginal",
            "CreateDate",
            "MediaCreateDate",
            "TrackCreateDate",
        ]:
            if keyword not in exif_data:
                continue
            date_and_time = _exif_datetime_data_to_datetime_obj(
                naive_date_and_time=exif_data[keyword], time_zone=time_zone
            )
            if isinstance(date_and_time, datetime.datetime):
                break
        if date_and_time is None:
            date_and_time_type = DateAndTimeType.BEST
            for keyword in [
                "ModifyDate",
                "MediaModifyDate",
                "TrackModifyDate",
            ]:
                if keyword not in exif_data:
                    continue
                date_and_time = _exif_datetime_data_to_datetime_obj(
                    naive_date_and_time=exif_data[keyword],
                    time_zone=datetime.timezone.utc,
                )
                if isinstance(date_and_time, datetime.datetime):
                    break

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
