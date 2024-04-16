from __future__ import annotations

import dataclasses
import datetime
import enum
import json
import logging
import os
import statistics
import subprocess
from typing import Any, ClassVar


logger = logging.getLogger()


class DateAndTimeType(enum.Enum):
    # The actual time that the photo is taken / video is recorded / audio is recorded
    AUTHENTIC = "AUTHENTIC"
    # The earliest date and time information that could be found in the file's metadata. Yet, it is probably not the actual time we want
    BEST = "BEST"
    # A hard-coded date and time information
    CURATED = "CURATED"


class EditType(enum.Enum):
    ORIGINAL = "ORIGINAL"
    EDITED = "EDITED"


@dataclasses.dataclass
class MediaFileInfo:
    editing_softwares_keywords: ClassVar[list[str]] = dataclasses.field(
        default=[]
    )
    date_and_time_type: DateAndTimeType
    date_and_time: datetime.datetime
    suspected_editing_software_keywords: list[str] = dataclasses.field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        # Check if a datetime object is localized
        # Reference: https://stackoverflow.com/q/5802108
        assert self._is_datetime_object_timezone_aware(
            datetime_object=self.date_and_time
        )
        self.suspected_editing_software_keywords = [
            str(i).lower() for i in self.suspected_editing_software_keywords
        ]

    @property
    def is_edited(self) -> bool:
        is_edited = False
        for keyword in type(self).editing_softwares_keywords:
            keyword_lowercase = keyword.lower()
            for test_sample in self.suspected_editing_software_keywords:
                if keyword_lowercase in test_sample:
                    is_edited = True
                    break
        return is_edited

    @property
    def edit_type(self) -> EditType:
        return EditType.EDITED if self.is_edited else EditType.ORIGINAL

    @classmethod
    def from_file_status(cls, file_path: str) -> MediaFileInfo:
        date_and_time = datetime.datetime.fromtimestamp(
            os.stat(file_path).st_mtime, tz=datetime.timezone.utc
        )
        return cls(
            date_and_time_type=DateAndTimeType.BEST,
            date_and_time=date_and_time,
        )

    @staticmethod
    def get_exiftool_output(file_path: str) -> dict[str, Any]:
        command = ["exiftool", "-ExtractEmbedded", "-j", file_path]
        result_bytes = subprocess.check_output(command)
        result_str = result_bytes.decode("UTF-8").rstrip("\r\n")
        try:
            result = json.loads(result_str)[0]
        except:
            result = {}
        return result

    @staticmethod
    def _is_datetime_object_timezone_aware(
        datetime_object: datetime.datetime,
    ) -> bool:
        return (
            datetime_object.tzinfo is not None
            and datetime_object.tzinfo.utcoffset(datetime_object) is not None
        )

    @staticmethod
    def _get_min_datetime(*args) -> datetime.datetime:
        candidates = [
            arg for arg in args if isinstance(arg, datetime.datetime)
        ]
        if len(candidates) == 0:
            return None
        return min(candidates)

    @staticmethod
    def _poll(*args):
        assert len(args) > 0
        assert all([isinstance(i, type(args[0])) for i in args])
        return statistics.mode(args)
