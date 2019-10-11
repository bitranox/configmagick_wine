# ### STDLIB
import pathlib
import subprocess
import time
from typing import Union

# ### OWN
import configmagick_linux
import lib_log_utils


# ####### PROJ

try:
    # imports for local pytest
    from . import lib_wine             # type: ignore # pragma: no cover
except ImportError:                    # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                    # type: ignore # pragma: no cover


def install_wine_mono(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                      username: str = configmagick_linux.get_current_username()) -> None:
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    mono_msi_filename = get_path_mono_msi_filename(wine_prefix=wine_prefix)
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    lib_log_utils.banner_debug('Installing Wine Mono :\n'
                               'WINEPREFIX="{wine_prefix}"\n'
                               'WINEARCH="{wine_arch}"\n'
                               'mono_msi_filename="{mono_msi_filename}"\n'
                               'wine_cache_directory="{wine_cache_directory}"'
                               .format(wine_prefix=wine_prefix,
                                       wine_arch=wine_arch,
                                       wine_cache_directory=wine_cache_directory,
                                       mono_msi_filename=mono_msi_filename))

    download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=False)
    configmagick_linux.run_shell_command('WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{wine_cache_directory}/{mono_msi_filename}"'
                                         .format(wine_prefix=wine_prefix,
                                                 wine_arch=wine_arch,
                                                 wine_cache_directory=wine_cache_directory,
                                                 mono_msi_filename=mono_msi_filename))
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def download_mono_msi_files(wine_prefix: Union[str, pathlib.Path], username: str, force_download: bool = False) -> None:
    """
    >>> # TODO: TESTS VERALLGEMEINERN
    >>> wine_prefix = '/home/consul/.wine'
    >>> username = 'consul'
    >>> force_download = True
    >>> download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=force_download)
    >>> force_download = False
    >>> download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=force_download)

    """

    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    path_mono_msi_filename = get_path_mono_msi_filename(wine_prefix=wine_prefix)
    if not lib_wine.is_file_in_wine_cache(username=username, filename=path_mono_msi_filename) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=path_mono_msi_filename, username=username)
        mono_download_link = get_wine_mono_download_link_from_msi_filename(path_mono_msi_filename=path_mono_msi_filename)
        mono_download_link_backup = get_wine_mono_download_backup_link_from_msi_filename(path_mono_msi_filename=path_mono_msi_filename)
        try:
            lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=path_mono_msi_filename, username=username)
        except subprocess.CalledProcessError:
            lib_wine.download_file_to_winecache(download_link=mono_download_link_backup, filename=path_mono_msi_filename, username=username)


def get_path_mono_msi_filename(wine_prefix: pathlib.Path) -> pathlib.Path:
    """
    >>> ### TODO - TESTS
    >>> get_path_mono_msi_filename(pathlib.Path('/home/consul/.wine'))
    PosixPath('wine-mono-4.9.3.msi')

    """
    path_appwiz = wine_prefix / 'drive_c/windows/system32/appwiz.cpl'
    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Mono MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))
    strings_command = configmagick_linux.get_bash_command('strings')
    print(strings_command.command_string)
    print(strings_command.command_type)
    response = configmagick_linux.run_shell_command('{strings_command_string} -n 12 "{path_appwiz}" | grep wine-mono | grep .msi'
                                                    .format(strings_command_string=strings_command.command_string,
                                                            path_appwiz=path_appwiz), shell=True, quiet=True)
    mono_msi_filename = response.stdout
    if not mono_msi_filename:
        raise RuntimeError('can not determine Mono MSI Filename from WINEPREFIX="wine_prefix"'
                           .format(wine_prefix=wine_prefix))
    path_mono_msi = pathlib.Path(mono_msi_filename)
    return path_mono_msi


def get_wine_mono_download_link_from_msi_filename(path_mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> result = get_wine_mono_download_link_from_msi_filename(path_mono_msi_filename='wine-mono-4.9.3.msi')
    >>> assert result == 'https://source.winehq.org/winemono.php?v=4.9.3'
    """
    mono_version = get_mono_version_from_msi_filename(path_mono_msi_filename=path_mono_msi_filename)
    wine_mono_download_link = 'https://source.winehq.org/winemono.php?v={mono_version}'.format(mono_version=mono_version)
    return wine_mono_download_link


def get_wine_mono_download_backup_link_from_msi_filename(path_mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> result = get_wine_mono_download_backup_link_from_msi_filename(path_mono_msi_filename='wine-mono-4.9.3.msi')
    >>> assert result == 'https://dl.winehq.org/wine/wine-mono/4.9.3/wine-mono-4.9.3.msi'
    """
    mono_version = get_mono_version_from_msi_filename(path_mono_msi_filename=path_mono_msi_filename)
    wine_mono_download_backup_link = 'https://dl.winehq.org/wine/wine-mono/{mono_version}/{path_mono_msi_filename}'\
        .format(mono_version=mono_version, path_mono_msi_filename=path_mono_msi_filename)
    return wine_mono_download_backup_link


def get_mono_version_from_msi_filename(path_mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> assert get_mono_version_from_msi_filename(path_mono_msi_filename='wine-mono-4.9.3.msi') == '4.9.3'
    """
    mono_msi_filename = str(path_mono_msi_filename)
    mono_version = mono_msi_filename.rsplit('-', 1)[1]
    mono_version = mono_version.rsplit('.', 1)[0]
    return mono_version
