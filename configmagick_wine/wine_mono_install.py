# ### STDLIB
import pathlib
import subprocess
from typing import Union

# ### OWN
import configmagick_linux
import lib_log_utils
import lib_shell

# ####### PROJ
try:
    # imports for local pytest
    from . import lib_wine              # type: ignore # pragma: no cover
    from . import wine_install          # type: ignore # pragma: no cover
    from . import wine_machine_install  # type: ignore # pragma: no cover
except ImportError:                     # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                     # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_install                 # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_machine_install                 # type: ignore # pragma: no cover


def install_wine_mono_latest(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                             username: str = configmagick_linux.get_current_username(), quiet: bool = False) -> None:
    """
    install the latest mono version from github

    >>> wine_machine_install.create_wine_test_prefixes()
    >>> install_wine_mono_latest('wine_test_32', quiet=True)
    >>> install_wine_mono_latest('wine_test_64', quiet=True)

    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    mono_download_link = get_wine_mono_download_link_from_github()
    mono_msi_filename = pathlib.Path(mono_download_link.rsplit('/', 1)[1])
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    lib_log_utils.banner_verbose('Installing Wine Mono :\n'
                                 'WINEPREFIX="{wine_prefix}"\n'
                                 'WINEARCH="{wine_arch}"\n'
                                 'mono_msi_filename="{mono_msi_filename}"\n'
                                 'wine_cache_directory="{wine_cache_directory}"'
                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         wine_cache_directory=wine_cache_directory,
                                         mono_msi_filename=mono_msi_filename),
                                 quiet=quiet)

    download_latest_mono_msi_files_from_github(username=username, force_download=False, quiet=quiet)

    lib_log_utils.log_verbose('Install "{mono_msi_filename}" on WINEPREFIX="{wine_prefix}"'
                              .format(mono_msi_filename=mono_msi_filename, wine_prefix=wine_prefix),
                              quiet=quiet)

    command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{wine_cache_directory}/{mono_msi_filename}"'\
        .format(wine_prefix=wine_prefix,
                wine_arch=wine_arch,
                wine_cache_directory=wine_cache_directory,
                mono_msi_filename=mono_msi_filename)
    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def install_wine_mono_recommended(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                                  username: str = configmagick_linux.get_current_username(), quiet: bool = False) -> None:
    """ Installs the mono version stated in appwiz.cpl - might be not the newest version, se we should prefer to install the latest wine-mono from github
    Mono version can only be extracted from wine prefixes created with wine version 4.18 upwards, on older version this does not work

    >>> wine_machine_install.create_wine_test_prefixes()
    >>> install_wine_mono_recommended('wine_test_32', quiet=True)
    >>> install_wine_mono_recommended('wine_test_64', quiet=True)

    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    mono_msi_filename = get_mono_msi_filename_from_appwiz(wine_prefix=wine_prefix, username=username)
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    lib_log_utils.banner_verbose('Installing Wine Mono :\n'
                                 'WINEPREFIX="{wine_prefix}"\n'
                                 'WINEARCH="{wine_arch}"\n'
                                 'mono_msi_filename="{mono_msi_filename}"\n'
                                 'wine_cache_directory="{wine_cache_directory}"'
                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         wine_cache_directory=wine_cache_directory,
                                         mono_msi_filename=mono_msi_filename),
                                 quiet=quiet)

    download_mono_msi_files_from_appwiz(wine_prefix=wine_prefix, username=username, force_download=False, quiet=quiet)

    command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{wine_cache_directory}/{mono_msi_filename}"'\
        .format(wine_prefix=wine_prefix,
                wine_arch=wine_arch,
                wine_cache_directory=wine_cache_directory,
                mono_msi_filename=mono_msi_filename)

    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def download_latest_mono_msi_files_from_github(username: str, force_download: bool = False, quiet: bool = False) -> None:
    """
    >>> username = configmagick_linux.get_current_username()
    >>> force_download = True
    >>> download_latest_mono_msi_files_from_github(username=username, force_download=force_download)
    >>> force_download = False
    >>> download_latest_mono_msi_files_from_github(username=username, force_download=force_download)
    """
    lib_log_utils.log_verbose('Download latest Mono MSI Files from Github to Wine Cache', quiet=quiet)
    mono_download_link = get_wine_mono_download_link_from_github()
    mono_msi_filename = pathlib.Path(mono_download_link.rsplit('/', 1)[1])

    if lib_wine.is_file_in_wine_cache(username=username, filename=mono_msi_filename) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=mono_msi_filename, username=username)
            lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=mono_msi_filename, username=username)
    else:
        lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=mono_msi_filename, username=username)


def download_mono_msi_files_from_appwiz(wine_prefix: Union[str, pathlib.Path], username: str, force_download: bool = False, quiet: bool = False) -> None:
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    mono_msi_filename = get_mono_msi_filename_from_appwiz(wine_prefix=wine_prefix, username=username)
    mono_download_link = get_wine_mono_download_link_from_msi_filename(mono_msi_filename=mono_msi_filename)
    mono_download_link_backup = get_wine_mono_download_backup_link_from_msi_filename(mono_msi_filename=mono_msi_filename)

    if lib_wine.is_file_in_wine_cache(username=username, filename=mono_msi_filename) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=mono_msi_filename, username=username)
            try:
                lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=mono_msi_filename, username=username)
            except subprocess.CalledProcessError:
                lib_wine.download_file_to_winecache(download_link=mono_download_link_backup, filename=mono_msi_filename, username=username)
    else:
        try:
            lib_wine.download_file_to_winecache(download_link=mono_download_link, filename=mono_msi_filename, username=username)
        except subprocess.CalledProcessError:
            lib_wine.download_file_to_winecache(download_link=mono_download_link_backup, filename=mono_msi_filename, username=username)


def get_mono_msi_filename_from_appwiz(wine_prefix: Union[str, pathlib.Path],
                                      username: str = configmagick_linux.get_current_username()) -> pathlib.Path:
    """
    >>> wine_machine_install.create_wine_test_prefixes()
    >>> username = configmagick_linux.get_current_username()
    >>> path_mono_msi_filename = get_mono_msi_filename_from_appwiz(wine_prefix='wine_test_32')
    >>> assert str(path_mono_msi_filename).startswith('wine-mono-') and str(path_mono_msi_filename).endswith('.msi')
    >>> path_mono_msi_filename = get_mono_msi_filename_from_appwiz(wine_prefix='wine_test_64')
    >>> assert str(path_mono_msi_filename).startswith('wine-mono-') and str(path_mono_msi_filename).endswith('.msi')
    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    if wine_arch == 'win32':
        path_appwiz = wine_prefix / 'drive_c/windows/system32/appwiz.cpl'
    else:
        path_appwiz = wine_prefix / 'drive_c/windows/syswow64/appwiz.cpl'

    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Mono MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))

    # this fails from unknown reason on travis xenial !
    response = lib_shell.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | fgrep "wine-mono-" | fgrep ".msi"'
                                           .format(path_appwiz=path_appwiz), shell=True, quiet=True, use_sudo=True)
    mono_msi_filename = response.stdout

    if not mono_msi_filename:
        raise RuntimeError('can not determine Mono MSI Filename from WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
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
    filename = configmagick_linux.get_path_home_dir_current_user() / 'mono-latest-release.html'
    try:
        download_link = 'https://github.com/madewokherd/wine-mono/releases/latest'
        configmagick_linux.download_file(download_link=download_link, filename=filename)
        link = lib_shell.run_shell_command('fgrep ".msi" "{filename}" | fgrep "wine-mono" | fgrep "href="'
                                           .format(filename=filename), shell=True, quiet=True, use_sudo=True).stdout
        link = link.split('href="', 1)[1]
        link = 'https://github.com/' + link.split('"', 1)[0]
    finally:
        lib_shell.run_shell_command('rm -f "{filename}"'.format(filename=filename), shell=True, quiet=True, use_sudo=True)
    return str(link)


def get_mono_version_from_msi_filename(path_mono_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    >>> assert get_mono_version_from_msi_filename(path_mono_msi_filename='wine-mono-4.9.3.msi') == '4.9.3'
    """
    mono_msi_filename = str(path_mono_msi_filename)
    mono_version = mono_msi_filename.rsplit('-', 1)[1]
    mono_version = mono_version.rsplit('.', 1)[0]
    return mono_version
