<h2 id='rename-file-by-time-info'>rename-file-by-time-info</h2>

This is a CLI tool to rename files under a folder, according to the time that the file is born. That is, I want the file to be named by the time it's original copy is created.

This information does not exist in the metadata of most files, and the best guess would be the file's modified timestamp (mtime), assuming that the file has not been changed since it was created. For many media files, we have more information thanks to the Exif metadata inside these files. Devices (e.g. camera) creating these media files will usually store the timestamp of file creation in the Exif metadata, and it remains unchanged after normal media editing operations (e.g. Photoshop). Thus, we can extract this value and use it to name the media file.

This tool heavily relies on [ExifTool][ExifTool] to extract Exif metadata from media files. Thus, it is basically a wrapper of ExifTool. You have to download ExifTool yourself and add it to the search paths of executables, so that this tool can also executable ExifTool to obtained the extracted Exif metadata. If ExifTool does not exist on the system, this tool can only handle a few image types by extracting Exif metadata using the [Python Pillow](https://python-pillow.org/) library.

<h2 id='get-started.rename-file-by-time-info'>Get Started</h2>

<h3 id='windows.get-started.rename-file-by-time-info'>Windows</h3>

1. Download [Exiftool][ExifTool] Windows executable and rename the extracted executable from "exiftool(-k).exe" to "exiftool.exe".
1. Add the directory of "exiftool.exe" to "System Properties --> Advanced --> Environment Variables --> User variables --> Path".
1. Open terminal and run "exiftool -ver" to make sure comand "exiftool" is found by the system.
1. Download the latest version of this tool from the [GitHub Releases](https://github.com/dailyideas/rename-file-by-time-info/releases) page.
1. Extract this tool from the downloaded archive (e.g. rename_files-1.0.0-windows-amd64.tar.gz) and add the directory of "rename_files.exe" to "System Properties --> Advanced --> Environment Variables --> User variables --> Path".
1. Open terminal and run "rename_files --version" to make sure command "rename_files" is found by the system.

<h2 id='usage.rename-file-by-time-info'>Usage</h2>

```sh
rename_files [global_options] <subcommand> [subcommand_options] <target_directory>
```

`subcommand` should be either `general` or `media`. `global_options` are optional arguments that are universal across subcommands. `subcommand_options` are optional arguments that are specific to that subcommand. `target_directory` is the path to the directory that this command going to work on.

<h3 id='basic-usage.usage.rename-file-by-time-info'>Basic Usage</h3>

- Run `rename_files general .` to rename all files under the current directory, according to their modified timestamp.
- Run `rename_files media .` to renames supported media files under the current directory, according to datetime information embedded in their metadata. Whether a file will be treated as a media file is defined in the configuration file. See section [supported_file_extensions](#supported_file_extensions.configurations.rename-file-by-time-info) for more details.

<h3 id='available-arguments.rename-file-by-time-info'>Available Arguments</h3>

<h4 id='help.available-arguments.rename-file-by-time-info'>help</h4>

To get runtime help:

```sh
rename_files --help
```

<h4 id='version.available-arguments.rename-file-by-time-info'>version</h4>

To show the version of the tool:

```sh
rename_files --version
```

<h4 id='config-file.available-arguments.rename-file-by-time-info'>config-file</h4>

To specify the configuration file to be used (rather than loading configurations from config.json):

```sh
rename_files --config-file <file-path> <subcommand> [subcommand_options] <target_directory>
```

<h4 id='general.available-arguments.rename-file-by-time-info'>general</h4>

Use this subcommand to rename any files in a folder. Options for this subcommand are listed below:

| option | meaning | example |
| --- | --- | --- |
| `-r` | Rename files recursively ||
| `--forced-offset-time` | Specify a target timezone if the timezone of the timestamps used to rename the files are not what you expect. | `--forced-offset-time +08:00` |
| `--forced-date` | Specify the date of the files if the date information used to rename the files are not what you expect. | `--forced-date 2023-09-25` |
| `--exif-offset-time` | Specify the timezone of datetime data in Exif metadata if timezone information does not exist in the metadata. | `--exif-offset-time -04:00` |
| `--skip-files-with-formatted-names` | Specify this option so that files with name matching the naming format will be skipped. See section [configuration](#file_naming_format.configurations.rename-file-by-time-info) for more details. ||
| `--skip-media-files` | Specify this option so that files with extensions specified in [configuration file](#supported_file_extensions.configurations.rename-file-by-time-info) will be skipped. ||

<h4 id='media.available-arguments.rename-file-by-time-info'>media</h4>

Use this subcommand to rename media files. Options for this subcommand are listed below:

| option | meaning | example |
| --- | --- | --- |
| `-r` | Refer to [here](#general.available-arguments.rename-file-by-time-info) ||
| `--forced-offset-time` | Refer to [here](general.available-arguments.rename-file-by-time-info) ||
| `--forced-date` | Refer to [here](general.available-arguments.rename-file-by-time-info) ||
| `--exif-offset-time` | Refer to [here](general.available-arguments.rename-file-by-time-info) ||
| `--skip-files-with-formatted-names` | Refer to [here](general.available-arguments.rename-file-by-time-info) ||
| `--use-exiftool-on-images` or `--no-use-exiftool-on-images` | Specify either of these options to override [this](#use_exiftool_on_images.configurations.rename-file-by-time-info) field in the configuration file. ||

<h2 id='configurations.rename-file-by-time-info'>Configurations</h2>

After extracting this tool from the archive, you can find the JSON configuration file "config.json" along with the "rename_files.exe" executable. Configurable options are listed below.

<h3 id='file_naming_format.configurations.rename-file-by-time-info'>file_naming_format</h3>

Use format codes to specify the format of the file name.

<h4 id='general_file.file_naming_format.configurations.rename-file-by-time-info'>general_file</h4>

The following is the list of format codes available when parsing normal files (using the `general` sub-command).

| Directive | Meaning |
| --- | --- |
| %Y | 4-digit representation of the year.  |
| %y | 2-digit representation of the year within a century. |
| %m | 2-digit representation of the month |
| %d | 2-digit representation of the day of the month. |
| %H | 2-digit representation of the hour (24-hour clock). |
| %M | 2-digit representation of the minute. |
| %S | 2-digit representation of the second. |
| %z | UTC offset in the form ±HHMM |
| %{ms} | 3-digit representation of the millisecond. |
| %% | A literal '%' character. |

<h4 id='media_file.file_naming_format.configurations.rename-file-by-time-info'>media_file</h4>

Apart from the [format codes](#general_file.file_naming_format.configurations.rename-file-by-time-info) available when parsing normal files, the following has listed additional format codes available when parsing media files (using the `media` sub-command).

| Directive | Meaning | Remarks |
| --- | --- | --- |
| %{dtt} | A string to indicate what the date and time information in the file name is representing. | |
| %{et} | A string to indicate whether the media file has been edited before. | |

<h3 id='supported_file_extensions.configurations.rename-file-by-time-info'>supported_file_extensions</h3>

This section specifies the types of media files supported by different libraries used in this tool. You can remove items from the list if you do not want those types of files to be renamed when you using the `media` sub-command. Extensions in the list are case-insensitive.

<h4 id='exiftool.supported_file_extensions.configurations.rename-file-by-time-info'>exiftool</h4>

Specify the types of media files that will be passed to Exiftool for metadata extraction. Noted that image file extensions are located at a list separated from the video and audio file extensions.

<h4 id='pillow.supported_file_extensions.configurations.rename-file-by-time-info'>pillow</h4>

Specify the types of media files that will be passed to Python Pillow for metadata extraction.

<h3 id='ignored_file_extensions.configurations.rename-file-by-time-info'>ignored_file_extensions</h3>

File with extension specified in this list will not be renamed by this tool.

<h3 id='media.configurations.rename-file-by-time-info'>media</h3>

<h4 id='dateandtimetype.media.configurations.rename-file-by-time-info'>DateAndTimeType</h4>

This field maps the DateAndTimeType to a string that will be shown on the file name if you use the `%{dtt}` format code when parsing media files. DateAndTimeType is an enumeration with the following members:

| Member | Meaning |
| --- | --- |
| AUTHENTIC | The date and time information extracted from the metadata of the file is representing the actual time that the media (image, video or audio) is generated. |
| BEST | The earliest date and time information that can be found from the metadata of the file, but not necessarily the time that the media (image, video or audio) is generated. |
| CURATED | The date and time information is a hard-coded value. That is, the information is not retrieved from the metadata of the file. |

<h4 id='edittype.media.configurations.rename-file-by-time-info'>EditType</h4>

This field maps the EditType to a string that will be shown on the file name if you use the `%{et}` format code when parsing media files. EditType is an enumeration with the following members:

| Member | Meaning |
| --- | --- |
| ORIGINAL | It is likely that the file is an original copy of the media. |
| EDITED | It is likely that the file has been altered by editors (e.g. Photoshop) |

<h3 id='editing_softwares_keywords.configurations.rename-file-by-time-info'>editing_softwares_keywords</h3>

How this tool determine whether a media file has been edited is by finding the name of the editing softwares in the metadata of the file. Usually, a media file exported from an editing software will have it name embedded in the metadata of the file. This list specifies the texts that this tool will look for to determine whether the file is an exported file of an editing software.

<h3 id='use_exiftool_on_images.configurations.rename-file-by-time-info'>use_exiftool_on_images</h3>

By default, extraction of metadata from images is performed by Exiftool. However, the use of Exiftool in this tool has not been optimized in terms of speed. If all the types of files you want to process can be handled by Python Pillow, you may want to choose not to use Exiftool on images by specifying `"use_exiftool_on_images": false`.

<h3 id='debug_mode.configurations.rename-file-by-time-info'>debug_mode</h3>

Setting it to true will output more logs.

<h2 id='development.rename-file-by-time-info'>Development</h2>

<h3 id='distribute.development.rename-file-by-time-info'>Distribute</h3>

1. `pip install .[dist]`
1. `python -O distribute.py`
1. Distributable generated can be found in `dist`.

<h2 id='license.rename-file-by-time-info'>License</h2>

This project is licensed under the terms of the MIT license.

[ExifTool]: https://exiftool.org/
