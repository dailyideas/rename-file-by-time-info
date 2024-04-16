import argparse
import datetime
import json
import logging
import os

from rename_file_by_time_info import external_program, general_file, media_file
from rename_file_by_time_info._version import __version__


logger = logging.getLogger()
logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.INFO)


def _rename_general_files(
    files_paths: list[str], cli_args: argparse.Namespace, config_file: dict
) -> None:
    skip_extensions = (
        set()
        if cli_args.skip_media_files is False
        else set(
            [
                i.lower()
                for i in [
                    *config_file["supported_file_extensions"]["exiftool"][
                        "image"
                    ],
                    *config_file["supported_file_extensions"]["exiftool"][
                        "video_and_audio"
                    ],
                    *config_file["supported_file_extensions"]["pillow"][
                        "image"
                    ],
                    *config_file["ignored_file_extensions"],
                ]
            ]
        )
    )
    last_directory = None
    for file_path in files_paths:
        current_directory = os.path.dirname(file_path)
        if current_directory != last_directory:
            logger.info("Processing files in directory: %s", current_directory)
            last_directory = current_directory
        file_name_prefix, file_extension = (
            general_file.helper.get_file_name_prefix_and_extension(
                file_name_or_path=file_path
            )
        )
        if file_name_prefix[0] == ".":
            logger.info("Skip hidden file: %s", file_path)
            continue
        if file_extension.lower() in skip_extensions:
            logger.info("Skip specific file type: %s", file_path)
            continue
        general_file.helper.rename(
            file_path=file_path,
            naming_format=config_file["file_naming_format"]["general_file"],
            forced_offset_time=cli_args.forced_offset_time,
            forced_date=cli_args.forced_date,
            skip_if_file_name_matches_naming_format=cli_args.skip_files_with_formatted_names,
        )


def _rename_media_files(
    files_paths: list[str], cli_args: argparse.Namespace, config_file: dict
) -> None:
    try:
        exiftool_exists = (
            external_program.helper.execute(
                command=["exiftool", "-echo", "OK"]
            )
            == "OK"
        )
    except FileNotFoundError:
        exiftool_exists = False
    if exiftool_exists is False:
        logger.warning("\"exiftool\" not found")

    use_exiftool_on_images = (cli_args.use_exiftool_on_images is True) or (
        cli_args.use_exiftool_on_images is None
        and config_file["use_exiftool_on_images"] is True
    )
    image_file_extensions: list[str] = []
    video_and_audio_file_extensions: list[str] = []
    if exiftool_exists:
        if use_exiftool_on_images:
            image_file_extensions.extend(
                config_file["supported_file_extensions"]["exiftool"]["image"]
            )
        else:
            image_file_extensions.extend(
                config_file["supported_file_extensions"]["pillow"]["image"]
            )
        video_and_audio_file_extensions.extend(
            config_file["supported_file_extensions"]["exiftool"][
                "video_and_audio"
            ]
        )
    else:
        image_file_extensions.extend(
            config_file["supported_file_extensions"]["pillow"]["image"]
        )

    last_directory = None
    for file_path in files_paths:
        current_directory = os.path.dirname(file_path)
        if current_directory != last_directory:
            logger.info("Processing files in directory: %s", current_directory)
            last_directory = current_directory
        file_name_prefix, _ = (
            general_file.helper.get_file_name_prefix_and_extension(
                file_name_or_path=file_path
            )
        )
        if file_name_prefix[0] == ".":
            logger.info("Skip hidden file: %s", file_path)
            continue
        media_file.helper.rename(
            file_path=file_path,
            naming_format=config_file["file_naming_format"]["media_file"],
            forced_offset_time=cli_args.forced_offset_time,
            forced_date=cli_args.forced_date,
            exif_offset_time=cli_args.exif_offset_time,
            use_exiftool_on_images=use_exiftool_on_images,
            image_file_extensions=image_file_extensions,
            video_and_audio_file_extensions=video_and_audio_file_extensions,
            skip_if_file_name_matches_naming_format=cli_args.skip_files_with_formatted_names,
        )


def main(cli_args: argparse.Namespace, config_file: dict) -> None:
    if cli_args.r is True:
        # Search files recursively
        files_paths = []
        for root, dirs, files in os.walk(cli_args.src):
            files_paths.extend([os.path.join(root, f) for f in files])
    else:
        # Non-recursive search
        potential_paths = [
            os.path.join(cli_args.src, f) for f in os.listdir(cli_args.src)
        ]
        files_paths = [p for p in potential_paths if os.path.isfile(p)]
    files_paths.sort()

    if cli_args.subcommand == "general":
        _rename_general_files(
            files_paths=files_paths, cli_args=cli_args, config_file=config_file
        )
    elif cli_args.subcommand == "media":
        _rename_media_files(
            files_paths=files_paths, cli_args=cli_args, config_file=config_file
        )
    else:
        raise NotImplementedError()


if __name__ == "__main__":
    # Reference: https://stackoverflow.com/q/7498595
    parser = argparse.ArgumentParser(
        description="Rename files", allow_abbrev=False
    )
    # Reference: https://stackoverflow.com/q/15405636
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--config-file",
        type=str,
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.json"
        ),
    )
    subcommands_parent_parser = argparse.ArgumentParser(add_help=False)
    subcommands_parent_parser.add_argument(
        "-r", action="store_true", help="Rename files recursively"
    )
    subcommands_parent_parser.add_argument(
        "--forced-offset-time",
        type=str,
        default=None,
        help="The hardcoded offset time (timezone) of the files. Format: \"[+,-]HH:MM\"",
    )
    subcommands_parent_parser.add_argument(
        "--forced-date",
        type=lambda s: datetime.date.fromisoformat(s),
        default=None,
        help="Files will be renamed using this date. Format: YYYY-MM-DD",
    )
    subcommands_parent_parser.add_argument(
        "--exif-offset-time",
        type=str,
        default=None,
        help="The offset time (timezone) of Exif datetime data in the media files. Format: \"[+,-]HH:MM\"",
    )
    subcommands_parent_parser.add_argument(
        "--skip-files-with-formatted-names",
        action="store_true",
        help="Not to process files with names that have already matched the naming format",
    )
    subcommands_parent_parser.add_argument(
        "src",
        type=str,
        help="Source directory which contains files to be renamed",
    )
    subparser = parser.add_subparsers(dest="subcommand", required=True)
    rename_general_files_subparser = subparser.add_parser(
        "general", parents=[subcommands_parent_parser]
    )
    rename_general_files_subparser.add_argument(
        "--skip-media-files",
        action="store_true",
        help="Not to process media files",
    )
    rename_media_files_subparser = subparser.add_parser(
        "media", parents=[subcommands_parent_parser]
    )
    rename_media_files_subparser.add_argument(
        "--use-exiftool-on-images",
        action=argparse.BooleanOptionalAction,
        default=None,
        type=bool,
        help="Use exiftool to get Exif data from images",
    )
    cli_args = parser.parse_args()

    config_file = json.load(open(cli_args.config_file))

    logging.basicConfig(
        format=(
            "%(asctime)s %(levelname).1s %(name)s %(message)s"
            if config_file.get("debug_mode", None) is True
            else "%(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=(
            logging.DEBUG
            if config_file.get("debug_mode", None) is True
            else logging.INFO
        ),
    )

    media_file.MediaFileInfo.editing_softwares_keywords = config_file.get(
        "editing_softwares_keywords", []
    )
    date_and_time_type_to_value_mapping = {
        media_file.media_file_info.DateAndTimeType(k): v
        for k, v in config_file.get("media", {})
        .get("DateAndTimeType", {})
        .items()
    }
    media_file.MediaFileNameFormatter.update_date_and_time_type_to_value_mapping(
        mapping=date_and_time_type_to_value_mapping
    )
    media_file.MediaFileNameFormatter.set_regex_of_format_code(
        format_code=r"{dtt}",
        choices=date_and_time_type_to_value_mapping.values(),
    )
    edit_type_to_value_mapping = {
        media_file.media_file_info.EditType(k): v
        for k, v in config_file.get("media", {}).get("EditType", {}).items()
    }
    media_file.MediaFileNameFormatter.update_edit_type_to_value_mapping(
        mapping=edit_type_to_value_mapping
    )
    media_file.MediaFileNameFormatter.set_regex_of_format_code(
        format_code=r"{et}", choices=edit_type_to_value_mapping.values()
    )

    main(cli_args=cli_args, config_file=config_file)
