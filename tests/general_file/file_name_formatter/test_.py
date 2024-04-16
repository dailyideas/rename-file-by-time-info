import datetime

from rename_file_by_time_info import general_file


def test_get_formatted_filename():
    formatter = general_file.FileNameFormatter(
        year=6543,
        month=2,
        day=10,
        hour=12,
        minute=3,
        second=4,
        millisecond=567,
        timezone=datetime.timezone(offset=datetime.timedelta(hours=8)),
    )
    assert (
        formatter.get_formatted_filename(
            naming_format=r"^%Y%m%d%H%M%S%{ms}%z%%"
        )
        == "^65430210120304567+0800%"
    )
