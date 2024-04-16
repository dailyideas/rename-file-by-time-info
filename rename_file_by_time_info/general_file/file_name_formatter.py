import dataclasses
import datetime
from typing import ClassVar


class NoValueAssociatedWithTheFormatCodeError(ValueError):
    pass


@dataclasses.dataclass
class FileNameFormatter:
    FORMAT_CODES: ClassVar[set[str]] = set(
        ("Y", "y", "m", "d", "H", "M", "S", r"{ms}", "z")
    )

    _format_codes_to_regex_mapping: ClassVar[dict[str, str]] = {
        "Y": r"\d{4}",
        "y": r"\d{2}",
        "m": r"(0[1-9]|1[0-2])",
        "d": r"(0[1-9]|[1-2][0-9]|3[0-1])",
        "H": r"(0[0-9]|1[0-9]|2[0-3])",
        "M": r"(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])",
        "S": r"(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])",
        r"{ms}": r"\d{3}",
        "z": r"[+-](0[0-9]|1[0-9]|2[0-3])(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])",
    }

    year: int | None
    month: int | None
    day: int | None
    hour: int | None
    minute: int | None
    second: int | None
    millisecond: int | None
    timezone: datetime.timezone | None

    def __post_init__(self) -> None:
        format_codes_to_values_mapping: dict[str, str] = {
            i: None for i in type(self).FORMAT_CODES
        }
        format_codes_to_values_mapping["%"] = "%"
        if isinstance(self.year, int):
            assert self.year >= 0 and self.year <= 9999
            format_codes_to_values_mapping["Y"] = "{:04d}".format(self.year)
            format_codes_to_values_mapping["y"] = "{:02d}".format(
                self.year % 100
            )
        if isinstance(self.month, int):
            assert self.month >= 1 and self.month <= 12
            format_codes_to_values_mapping["m"] = "{:02d}".format(self.month)
        if isinstance(self.day, int):
            assert self.day >= 1 and self.day <= 31
            format_codes_to_values_mapping["d"] = "{:02d}".format(self.day)
        if isinstance(self.hour, int):
            assert self.hour >= 0 and self.hour <= 23
            format_codes_to_values_mapping["H"] = "{:02d}".format(self.hour)
        if isinstance(self.minute, int):
            assert self.minute >= 0 and self.minute <= 59
            format_codes_to_values_mapping["M"] = "{:02d}".format(self.minute)
        if isinstance(self.second, int):
            assert self.second >= 0 and self.second <= 59
            format_codes_to_values_mapping["S"] = "{:02d}".format(self.second)
        if isinstance(self.millisecond, int):
            assert self.millisecond >= 0 and self.millisecond <= 999
            format_codes_to_values_mapping[r"{ms}"] = "{:03d}".format(
                self.millisecond
            )
        else:
            format_codes_to_values_mapping[r"{ms}"] = "000"
        if isinstance(self.timezone, datetime.timezone):
            offset_time = self.timezone.tzname(None)
            # Reference: https://docs.python.org/3/library/datetime.html#datetime.timezone.tzname
            offset_time = "+00:00" if offset_time == "UTC" else offset_time[3:]
            # Hardcoded removal of the colon
            format_codes_to_values_mapping["z"] = offset_time.replace(":", "")
        self._format_code_to_value_mapping = format_codes_to_values_mapping

    @classmethod
    def set_regex_of_format_code(
        cls,
        format_code: str,
        choices: list[str] | None = None,
        regex: str | None = None,
    ) -> None:
        if choices is None and regex is None:
            raise ValueError(
                "Either \"choices\" or \"regex\" must be specified"
            )
        cls._format_codes_to_regex_mapping[format_code] = "({})".format(
            "|".join(choices) if choices is not None else regex
        )

    @classmethod
    def get_regex_of_naming_format(cls, naming_format: str) -> bool:
        regex = []
        i = 0
        try:
            while i < len(naming_format):
                if naming_format[i] != "%":
                    regex.append(naming_format[i])
                    i += 1
                    continue
                j = i + 1
                if j >= len(naming_format):
                    raise ValueError()
                format_code = naming_format[j]
                if format_code == r"{":
                    j += 1
                    while j < len(naming_format) and naming_format[j] != r"}":
                        j += 1
                    if naming_format[j] != r"}":
                        raise ValueError()
                    format_code = naming_format[i + 1 : j + 1]
                if format_code not in cls.FORMAT_CODES:
                    raise ValueError()
                regex.append(cls._format_codes_to_regex_mapping[format_code])
                i = j + 1
        except ValueError:
            raise ValueError("Invalid format string: {}".format(naming_format))
        return "".join(regex)

    def get_formatted_filename(self, naming_format: str) -> str:
        file_name = []
        i = 0
        try:
            while i < len(naming_format):
                if naming_format[i] != "%":
                    file_name.append(naming_format[i])
                    i += 1
                    continue
                j = i + 1
                if j >= len(naming_format):
                    raise ValueError()
                format_code = naming_format[j]
                if format_code == r"{":
                    j += 1
                    while j < len(naming_format) and naming_format[j] != r"}":
                        j += 1
                    if naming_format[j] != r"}":
                        raise ValueError()
                    format_code = naming_format[i + 1 : j + 1]
                if format_code not in self._format_code_to_value_mapping:
                    raise ValueError()
                if self._format_code_to_value_mapping[format_code] is None:
                    raise NoValueAssociatedWithTheFormatCodeError()
                file_name.append(
                    self._format_code_to_value_mapping[format_code]
                )
                i = j + 1
        except NoValueAssociatedWithTheFormatCodeError:
            raise ValueError(
                "No value associated with the format code: {}".format(
                    format_code
                )
            )
        except ValueError:
            raise ValueError("Invalid format string: {}".format(naming_format))
        return "".join(file_name)
