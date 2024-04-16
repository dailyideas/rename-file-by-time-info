import dataclasses
from typing import ClassVar

from . import media_file_info
from rename_file_by_time_info import general_file


@dataclasses.dataclass
class MediaFileNameFormatter(general_file.FileNameFormatter):
    ADDITIONAL_FORMAT_CODES: ClassVar[set[str]] = set((r"{dtt}", r"{et}"))
    FORMAT_CODES: ClassVar[set[str]] = (
        general_file.FileNameFormatter.FORMAT_CODES | ADDITIONAL_FORMAT_CODES
    )

    _date_and_time_type_to_value_mapping: ClassVar[
        dict[media_file_info.DateAndTimeType, str]
    ] = {}
    _edit_type_to_value_mapping: ClassVar[
        dict[media_file_info.EditType, str]
    ] = {}

    date_and_time_type: media_file_info.DateAndTimeType | None
    edit_type: media_file_info.EditType | None

    def __post_init__(self) -> None:
        super().__post_init__()

        format_codes_to_values_mapping: dict[str, str] = {
            i: None for i in type(self).ADDITIONAL_FORMAT_CODES
        }
        if isinstance(
            self.date_and_time_type, media_file_info.DateAndTimeType
        ):
            format_codes_to_values_mapping[r"{dtt}"] = type(
                self
            )._date_and_time_type_to_value_mapping[self.date_and_time_type]
        if isinstance(self.edit_type, media_file_info.EditType):
            format_codes_to_values_mapping[r"{et}"] = type(
                self
            )._edit_type_to_value_mapping[self.edit_type]
        self._format_code_to_value_mapping.update(
            format_codes_to_values_mapping
        )

    @classmethod
    def update_date_and_time_type_to_value_mapping(
        cls, mapping: dict[media_file_info.DateAndTimeType, str]
    ) -> None:
        cls._date_and_time_type_to_value_mapping.update(mapping)

    @classmethod
    def update_edit_type_to_value_mapping(
        cls, mapping: dict[media_file_info.EditType, str]
    ) -> None:
        cls._edit_type_to_value_mapping.update(mapping)
