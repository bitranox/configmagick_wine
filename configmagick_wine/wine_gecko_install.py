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
    from . import lib_wine             # type: ignore # pragma: no cover
    from . import wine_install
    from . import wine_machine_install
except ImportError:                    # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                    # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_install                # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_machine_install        # type: ignore # pragma: no cover


def install_wine_gecko(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                       username: str = configmagick_linux.get_current_username(),
                       quiet: bool = False) -> None:
    """
    install 32 Bit Gecko for 32/64 Bit Wine, and 64 Bit Gecko for 64 Bit Wine

    >>> wine_machine_install.create_wine_test_prefixes()
    >>> install_wine_gecko(wine_prefix='wine_test_32', quiet=True)
    >>> install_wine_gecko(wine_prefix='wine_test_64', quiet=True)

    """
    lib_log_utils.banner_verbose('Install Gecko on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix), quiet=quiet)
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    download_gecko_msi_files(wine_prefix=wine_prefix, username=username, quiet=True)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix, username)

    if wine_arch == 'win32' or wine_arch == 'win64':
        lib_log_utils.log_verbose('Install Gecko 32 Bit on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix), quiet=quiet)
        install_gecko_32(wine_prefix=wine_prefix, username=username, quiet=quiet)

    if wine_arch == 'win64':
        lib_log_utils.log_verbose('Install Gecko 64 Bit on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix), quiet=quiet)
        install_gecko_64(wine_prefix=wine_prefix, username=username, quiet=quiet)

    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case
    lib_log_utils.banner_success('Wine Gecko installed')


def install_gecko_32(wine_prefix: Union[str, pathlib.Path], username: str, quiet: bool = False) -> None:
    path_gecko_32_msi_filename = get_gecko_32_filename_from_appwiz(wine_prefix, username)
    install_gecko_by_architecture(wine_prefix, username, path_gecko_32_msi_filename, quiet=quiet)


def install_gecko_64(wine_prefix: Union[str, pathlib.Path], username: str, quiet: bool = False) -> None:
    path_gecko_64_msi_filename = get_gecko_64_filename_from_appwiz(wine_prefix, username)
    install_gecko_by_architecture(wine_prefix, username, path_gecko_64_msi_filename, quiet=quiet)


def install_gecko_by_architecture(wine_prefix: Union[str, pathlib.Path], username: str, path_gecko_msi_filename: pathlib.Path, quiet: bool = False) -> None:
    path_wine_cache = lib_wine.get_path_wine_cache_for_user(username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix, username)

    command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{path_wine_cache}/{path_gecko_msi_filename}"'.format(
        wine_prefix=wine_prefix,
        wine_arch=wine_arch,
        path_wine_cache=path_wine_cache,
        path_gecko_msi_filename=path_gecko_msi_filename)

    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)


def download_gecko_msi_files(wine_prefix: Union[str, pathlib.Path], username: str, quiet: bool = False) -> None:

    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix, username)
    if wine_arch == 'win32' or wine_arch == 'win64':
        download_gecko_32_msi_files(wine_prefix, username, quiet=quiet)
    if wine_arch == 'win64':
        download_gecko_64_msi_files(wine_prefix, username, quiet=quiet)
    lib_wine.fix_permissions_winecache(username=username)


def download_gecko_32_msi_files(wine_prefix: Union[str, pathlib.Path], username: str, quiet: bool = False) -> None:
    path_wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username)
    path_gecko_32_msi_filename = get_gecko_32_filename_from_appwiz(wine_prefix, username)
    gecko_download_link = get_gecko_download_link(path_gecko_32_msi_filename)
    gecko_backup_download_link = get_gecko_backup_download_link(path_gecko_32_msi_filename)
    try:
        configmagick_linux.download_file(gecko_download_link, path_wine_cache_directory / path_gecko_32_msi_filename, use_sudo=True, quiet=quiet)
    except subprocess.CalledProcessError:
        configmagick_linux.download_file(gecko_backup_download_link, path_wine_cache_directory / path_gecko_32_msi_filename, use_sudo=True, quiet=quiet)


def download_gecko_64_msi_files(wine_prefix: Union[str, pathlib.Path], username: str, quiet: bool = False) -> None:
    path_wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username)
    path_gecko_64_msi_filename = get_gecko_64_filename_from_appwiz(wine_prefix, username)
    gecko_download_link = get_gecko_download_link(path_gecko_64_msi_filename)
    gecko_backup_download_link = get_gecko_backup_download_link(path_gecko_64_msi_filename)
    try:
        configmagick_linux.download_file(gecko_download_link, path_wine_cache_directory / path_gecko_64_msi_filename, use_sudo=True, quiet=quiet)
    except subprocess.CalledProcessError:
        configmagick_linux.download_file(gecko_backup_download_link, path_wine_cache_directory / path_gecko_64_msi_filename, use_sudo=True, quiet=quiet)


def get_gecko_download_link(path_gecko_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    wine_gecko-2.47-x86.msi --> 'https://dl.winehq.org/wine/wine-gecko/2.47/wine_gecko-2.47-x86.msi'

    >>> assert get_gecko_download_link(pathlib.Path('wine_gecko-2.47-x86.msi')) == 'https://source.winehq.org/winegecko.php?v=2.47&arch=x86'
    >>> assert get_gecko_download_link(pathlib.Path('wine_gecko-2.47-x86_64.msi')) == 'https://source.winehq.org/winegecko.php?v=2.47&arch=x86_64'
    """
    gecko_version = get_gecko_version_from_path_gecko_msi_filename(path_gecko_msi_filename)
    gecko_arch = get_gecko_arch_from_path_gecko_msi_filename(path_gecko_msi_filename)
    gecko_download_link = 'https://source.winehq.org/winegecko.php?v={gecko_version}&arch={gecko_arch}'\
        .format(gecko_version=gecko_version, gecko_arch=gecko_arch)
    return gecko_download_link


def get_gecko_backup_download_link(path_gecko_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    wine_gecko-2.47-x86.msi --> 'https://dl.winehq.org/wine/wine-gecko/2.47/wine_gecko-2.47-x86.msi'

    >>> assert get_gecko_backup_download_link(pathlib.Path('wine_gecko-2.47-x86.msi'))\
                            == 'https://dl.winehq.org/wine/wine-gecko/2.47/wine_gecko-2.47-x86.msi'
    >>> assert get_gecko_backup_download_link(pathlib.Path('wine_gecko-2.47-x86_64.msi'))\
                            == 'https://dl.winehq.org/wine/wine-gecko/2.47/wine_gecko-2.47-x86_64.msi'
    """
    gecko_version = get_gecko_version_from_path_gecko_msi_filename(path_gecko_msi_filename)
    gecko_backup_download_link = 'https://dl.winehq.org/wine/wine-gecko/{gecko_version}/{path_gecko_msi_filename}'\
        .format(gecko_version=gecko_version, path_gecko_msi_filename=path_gecko_msi_filename)
    return gecko_backup_download_link


def get_gecko_version_from_path_gecko_msi_filename(path_gecko_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    wine_gecko-2.47-x86.msi --> 2.47

    >>> assert get_gecko_version_from_path_gecko_msi_filename(pathlib.Path('wine_gecko-2.47-x86.msi')) == '2.47'
    """
    gecko_version = str(path_gecko_msi_filename).split('-')[1]
    return gecko_version


def get_gecko_arch_from_path_gecko_msi_filename(path_gecko_msi_filename: Union[str, pathlib.Path]) -> str:
    """
    wine_gecko-2.47-x86.msi --> x86
    wine_gecko-2.47-x86_64.msi --> x86_64

    >>> assert get_gecko_arch_from_path_gecko_msi_filename(pathlib.Path('wine_gecko-2.47-x86.msi')) == 'x86'
    >>> assert get_gecko_arch_from_path_gecko_msi_filename(pathlib.Path('wine_gecko-2.47-x86_64.msi')) == 'x86_64'
    """
    gecko_arch = str(path_gecko_msi_filename).split('-')[2]
    gecko_arch = gecko_arch.split('.')[0]
    return gecko_arch


def get_gecko_32_filename_from_appwiz(wine_prefix: Union[str, pathlib.Path],
                                      username: str = configmagick_linux.get_current_username()) -> pathlib.Path:
    """ Gecko Filename can only be extracted from wine prefixes created with wine version 4.18 upwards,
    on older version this does not work and we assume gecko-2.47

    >>> wine_machine_install.create_wine_test_prefixes()

    >>> username = configmagick_linux.get_current_username()
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix='wine_test_32')
    >>> path_gecko_32_filename = get_gecko_32_filename_from_appwiz(wine_prefix)
    >>> assert str(path_gecko_32_filename).startswith('wine_gecko-') and str(path_gecko_32_filename).endswith('-x86.msi')
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_64')
    >>> path_gecko_32_filename = get_gecko_32_filename_from_appwiz(wine_prefix, username)
    >>> assert str(path_gecko_32_filename).startswith('wine_gecko-') and str(path_gecko_32_filename).endswith('-x86.msi')
    """
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    if wine_arch == 'win32':
        path_appwiz = pathlib.Path(wine_prefix) / 'drive_c/windows/system32/appwiz.cpl'
    else:
        path_appwiz = pathlib.Path(wine_prefix) / 'drive_c/windows/syswow64/appwiz.cpl'

    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Gecko MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))

    try:
        response = lib_shell.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | fgrep "wine_gecko-" | fgrep "x86.msi"'
                                               .format(path_appwiz=path_appwiz), shell=True, quiet=False, use_sudo=True)
        gecko_32_filename = response.stdout
    except (subprocess.CalledProcessError, RuntimeError):
        # this happens on old wine versions, the wine_gecko-2.47-x86.msi is not present in the appwiz.cpl
        lib_log_utils.log_warning('Can not determine Gecko Version from appwiz.cpl - assuming "wine_gecko-2.47-x86.msi"')
        gecko_32_filename = 'wine_gecko-2.47-x86.msi'

    path_gecko_32_filename = pathlib.Path(gecko_32_filename)
    return path_gecko_32_filename


def get_gecko_64_filename_from_appwiz(wine_prefix: Union[str, pathlib.Path],
                                      username: str = configmagick_linux.get_current_username()) -> pathlib.Path:
    """ Gecko 64 Bit Filename can only be read from a 64 Bit Wine Prefix
    Gecko Filename can only be extracted from wine prefixes created with wine version 4.18 upwards,
    on older version this does not work and we assume gecko-2.47


    >>> import unittest
    >>> wine_machine_install.create_wine_test_prefixes()
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_32')
    >>> unittest.TestCase().assertRaises(RuntimeError, get_gecko_64_filename_from_appwiz, wine_prefix)

    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_64')
    >>> path_gecko_64_filename = get_gecko_64_filename_from_appwiz(wine_prefix)
    >>> assert str(path_gecko_64_filename).startswith('wine_gecko-') and str(path_gecko_64_filename).endswith('-x86_64.msi')
    """
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    if wine_arch == 'win32':
        raise RuntimeError('can not determine Gecko 64 Bit msi Filename from a 32 Bit Wine Machine')
    else:
        path_appwiz = pathlib.Path(wine_prefix) / 'drive_c/windows/system32/appwiz.cpl'

    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Gecko MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))

    try:
        response = lib_shell.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | fgrep "wine_gecko" | fgrep "x86_64.msi"'
                                               .format(path_appwiz=path_appwiz), shell=True, quiet=True, use_sudo=True)
        gecko_64_filename = response.stdout
    except (subprocess.CalledProcessError, RuntimeError):
        # this happens on old wine versions, the wine_gecko-2.47-x86.msi is not present in the appwiz.cpl
        lib_log_utils.log_warning('Can not determine Gecko Version from appwiz.cpl - assuming "wine_gecko-2.47-x86_64.msi"')
        gecko_64_filename = 'wine_gecko-2.47-x86_64.msi'

    path_gecko_64_filename = pathlib.Path(gecko_64_filename)
    return path_gecko_64_filename
