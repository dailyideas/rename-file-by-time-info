import logging
import platform

import PyInstaller.__main__
import tarfile

from rename_file_by_time_info._version import __version__


logger = logging.getLogger()


def create_tar_gz(output_path: str, src_path: str) -> None:
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(src_path, arcname='')


logging.basicConfig(format="%(message)s", level=logging.INFO)


PyInstaller.__main__.run(
    [
        'rename_files.py',
        '--clean',
        '--noconfirm',
        '--onedir',
        '--add-data=config.json:.',
    ]
)
output_path = 'dist/rename_files-{}-{}-{}.tar.gz'.format(
    __version__,
    platform.system().lower(),
    platform.machine().lower(),
)
create_tar_gz(output_path=output_path, src_path="dist/rename_files")
logger.info("Created file for distribution: %s", output_path)
