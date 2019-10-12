# ### STDLIB
import pathlib
import subprocess
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
    """
    install the latest mono version from github
    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    mono_download_link = get_wine_mono_download_link_from_github()
    mono_msi_filename = pathlib.Path(mono_download_link.rsplit('/', 1)[1])
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

    # TODO: see https://travis-ci.community/t/travis-functions-no-such-file-or-directory/2286/10

    download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=False)

    command = 'runuser -l {username} -c \'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{wine_cache_directory}/{mono_msi_filename}"\''\
        .format(username=username,
                wine_prefix=wine_prefix,
                wine_arch=wine_arch,
                wine_cache_directory=wine_cache_directory,
                mono_msi_filename=mono_msi_filename)

    response = configmagick_linux.run_shell_command(command, except_on_fail=False)
    lib_log_utils.log_critical(response.stdout)
    lib_log_utils.log_critical(response.stderr)
    lib_log_utils.log_critical(response.returncode)

    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def install_wine_mono_appwiz(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                             username: str = configmagick_linux.get_current_username()) -> None:
    """
    install the mono version stated in appwiz.cpl - that does not work on travis, maybe some encoding issues
    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    mono_msi_filename = get_mono_msi_filename_from_appwiz(wine_prefix=wine_prefix)
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
    command = 'runuser -l {username} -c \'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{wine_cache_directory}/{mono_msi_filename}"\''\
        .format(username=username,
                wine_prefix=wine_prefix,
                wine_arch=wine_arch,
                wine_cache_directory=wine_cache_directory,
                mono_msi_filename=mono_msi_filename)

    configmagick_linux.run_shell_command(command)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def download_mono_msi_files(wine_prefix: Union[str, pathlib.Path], username: str, force_download: bool = False) -> None:
    """
    download the latest mono version from github
    >>> # TODO: TESTS VERALLGEMEINERN
    >>> wine_prefix = '/home/consul/.wine'
    >>> username = 'consul'
    >>> force_download = True
    >>> download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=force_download)
    >>> force_download = False
    >>> download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=force_download)

    """

    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    mono_download_link = get_wine_mono_download_link_from_github()
    mono_msi_filename = pathlib.Path(mono_download_link.rsplit('/', 1)[1])

    if not lib_wine.is_file_in_wine_cache(username=username, filename=mono_msi_filename) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=mono_msi_filename, username=username)
            lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=mono_msi_filename, username=username)


def download_mono_msi_files_appwiz(wine_prefix: Union[str, pathlib.Path], username: str, force_download: bool = False) -> None:
    """
    download the mono version stated in appwiz.cpl - that does not work on travis, maybe some encoding issues
    >>> # TODO: TESTS VERALLGEMEINERN
    >>> wine_prefix = '/home/consul/.wine'
    >>> username = 'consul'
    >>> force_download = True
    >>> download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=force_download)
    >>> force_download = False
    >>> download_mono_msi_files(wine_prefix=wine_prefix, username=username, force_download=force_download)

    """

    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    mono_msi_filename = get_mono_msi_filename_from_appwiz(wine_prefix=wine_prefix)
    if not lib_wine.is_file_in_wine_cache(username=username, filename=mono_msi_filename) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=mono_msi_filename, username=username)
        mono_download_link = get_wine_mono_download_link_from_msi_filename(mono_msi_filename=mono_msi_filename)
        mono_download_link_backup = get_wine_mono_download_backup_link_from_msi_filename(mono_msi_filename=mono_msi_filename)
        try:
            lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=mono_msi_filename, username=username)
        except subprocess.CalledProcessError:
            lib_wine.download_file_to_winecache(download_link=mono_download_link_backup, filename=mono_msi_filename, username=username)


def get_mono_msi_filename_from_appwiz(wine_prefix: pathlib.Path) -> pathlib.Path:
    """
    >>> get_mono_msi_filename_from_appwiz(pathlib.Path('/home/consul/.wine'))
    PosixPath('wine-mono-4.9.3.msi')

    """
    path_appwiz = wine_prefix / 'drive_c/windows/system32/appwiz.cpl'
    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Mono MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))

    # this fails from unknown reason on travis xenial !
    response = configmagick_linux.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | grep wine-mono | grep .msi'
                                                    .format(path_appwiz=path_appwiz), shell=True, quiet=True)
    mono_msi_filename = response.stdout

    if not mono_msi_filename:
        raise RuntimeError('can not determine Mono MSI Filename from WINEPREFIX="wine_prefix"'
                           .format(wine_prefix=wine_prefix))
    path_mono_msi = pathlib.Path(mono_msi_filename)
    return path_mono_msi


def get_wine_mono_download_link_from_msi_filename(mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> result = get_wine_mono_download_link_from_msi_filename(mono_msi_filename='wine-mono-4.9.3.msi')
    >>> assert result == 'https://source.winehq.org/winemono.php?v=4.9.3'
    """
    mono_version = get_mono_version_from_msi_filename(path_mono_msi_filename=mono_msi_filename)
    wine_mono_download_link = 'https://source.winehq.org/winemono.php?v={mono_version}'.format(mono_version=mono_version)
    return wine_mono_download_link


def get_wine_mono_download_backup_link_from_msi_filename(mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> result = get_wine_mono_download_backup_link_from_msi_filename(mono_msi_filename='wine-mono-4.9.3.msi')
    >>> assert result == 'https://dl.winehq.org/wine/wine-mono/4.9.3/wine-mono-4.9.3.msi'
    """
    mono_version = get_mono_version_from_msi_filename(path_mono_msi_filename=mono_msi_filename)
    wine_mono_download_backup_link = 'https://dl.winehq.org/wine/wine-mono/{mono_version}/{path_mono_msi_filename}'\
        .format(mono_version=mono_version, path_mono_msi_filename=mono_msi_filename)
    return wine_mono_download_backup_link


def get_wine_mono_download_link_from_github() -> str:
    """
    >>> get_wine_mono_download_link_from_github()  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    'https://github.com//madewokherd/wine-mono/releases/download/wine-mono-.../wine-mono-...msi'

    """
    download_link = 'https://github.com/madewokherd/wine-mono/releases/latest'
    filename = configmagick_linux.get_path_home_dir_current_user() / 'mono-latest-release.html'
    configmagick_linux.download_file(download_link=download_link, filename=filename)

    link = configmagick_linux.run_shell_command('grep ".msi" "{filename}" | grep wine-mono | grep href='
                                                .format(filename=filename), shell=True, quiet=True).stdout
    link = link.split('href="', 1)[1]
    link = 'https://github.com/' + link.split('"', 1)[0]
    configmagick_linux.run_shell_command('rm -f "{filename}"'.format(filename=filename), shell=True, quiet=True)
    return link


def get_mono_version_from_msi_filename(path_mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> assert get_mono_version_from_msi_filename(path_mono_msi_filename='wine-mono-4.9.3.msi') == '4.9.3'
    """
    mono_msi_filename = str(path_mono_msi_filename)
    mono_version = mono_msi_filename.rsplit('-', 1)[1]
    mono_version = mono_version.rsplit('.', 1)[0]
    return mono_version
