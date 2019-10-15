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
                       username: str = configmagick_linux.get_current_username()) -> None:
    """
    install 32 Bit Gecko for 32/64 Bit Wine, and 64 Bit Gecko for 64 Bit Wine

    >>> wine_install.install_wine(wine_release='staging')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    OK
    ...
    >>> wine_machine_install.install_wine_machine(wine_prefix='wine_test_32',wine_arch='win32',\
                                                  overwrite_existing_wine_machine=True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Using winetricks ...

    >>> wine_machine_install.install_wine_machine(wine_prefix='wine_test_64',wine_arch='win64',\
                                                  overwrite_existing_wine_machine=True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ---...
    You are using a 64-bit WINEPREFIX. ...


    >>> username = configmagick_linux.get_current_username()
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_32', username=username)
    >>> install_wine_gecko('wine_test_32', username=username)

    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_64', username=username)
    >>> install_wine_gecko('wine_test_64', username=username)


    """

    lib_log_utils.log_verbose('Install Gecko on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    download_gecko_msi_files(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix, username)

    if wine_arch == 'win32' or wine_arch == 'win64':
        lib_log_utils.log_verbose('Install Gecko 32 Bit on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
        install_gecko_32(wine_prefix, username)

    if wine_arch == 'win64':
        lib_log_utils.log_verbose('Install Gecko 64 Bit on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
        install_gecko_64(wine_prefix, username)

    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def install_gecko_32(wine_prefix: Union[str, pathlib.Path], username: str) -> None:
    path_gecko_32_msi_filename = get_gecko_32_filename_from_appwiz(wine_prefix, username)
    install_gecko_by_architecture(wine_prefix, username, path_gecko_32_msi_filename)


def install_gecko_64(wine_prefix: Union[str, pathlib.Path], username: str) -> None:
    path_gecko_64_msi_filename = get_gecko_64_filename_from_appwiz(wine_prefix, username)
    install_gecko_by_architecture(wine_prefix, username, path_gecko_64_msi_filename)


def install_gecko_by_architecture(wine_prefix: Union[str, pathlib.Path], username: str, path_gecko_msi_filename: pathlib.Path) -> None:
    path_wine_cache = lib_wine.get_path_wine_cache_for_user(username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix, username)
    configmagick_linux.run_shell_command(
        'runuser -l {username} -c \'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine msiexec /i "{path_wine_cache}/{path_gecko_msi_filename}"\''.format(
            username=username, wine_prefix=wine_prefix, wine_arch=wine_arch, path_wine_cache=path_wine_cache, path_gecko_msi_filename=path_gecko_msi_filename
        ))


def download_gecko_msi_files(wine_prefix: Union[str, pathlib.Path], username: str) -> None:

    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix, username)
    if wine_arch == 'win32' or wine_arch == 'win64':
        download_gecko_32_msi_files(wine_prefix, username)
    if wine_arch == 'win64':
        download_gecko_64_msi_files(wine_prefix, username)


def download_gecko_32_msi_files(wine_prefix: Union[str, pathlib.Path], username: str) -> None:
    path_wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username)
    path_gecko_32_msi_filename = get_gecko_32_filename_from_appwiz(wine_prefix, username)
    gecko_download_link = get_gecko_download_link(path_gecko_32_msi_filename)
    gecko_backup_download_link = get_gecko_backup_download_link(path_gecko_32_msi_filename)
    try:
        configmagick_linux.download_file(gecko_download_link, path_wine_cache_directory / path_gecko_32_msi_filename)
    except subprocess.CalledProcessError:
        configmagick_linux.download_file(gecko_backup_download_link, path_wine_cache_directory / path_gecko_32_msi_filename)


def download_gecko_64_msi_files(wine_prefix: Union[str, pathlib.Path], username: str) -> None:
    path_wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username)
    path_gecko_64_msi_filename = get_gecko_64_filename_from_appwiz(wine_prefix, username)
    gecko_download_link = get_gecko_download_link(path_gecko_64_msi_filename)
    gecko_backup_download_link = get_gecko_backup_download_link(path_gecko_64_msi_filename)
    try:
        configmagick_linux.download_file(gecko_download_link, path_wine_cache_directory / path_gecko_64_msi_filename)
    except subprocess.CalledProcessError:
        configmagick_linux.download_file(gecko_backup_download_link, path_wine_cache_directory / path_gecko_64_msi_filename)


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


def get_gecko_32_filename_from_appwiz(wine_prefix: Union[str, pathlib.Path], username: str) -> pathlib.Path:
    """
    >>> wine_install.install_wine(wine_release='staging')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    OK
    ...
    >>> wine_machine_install.install_wine_machine(wine_prefix='wine_test_32',wine_arch='win32',\
                                                  overwrite_existing_wine_machine=True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Using winetricks ...

    >>> wine_machine_install.install_wine_machine(wine_prefix='wine_test_64',wine_arch='win64',\
                                                  overwrite_existing_wine_machine=True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ---...
    You are using a 64-bit WINEPREFIX. ...


    >>> username = configmagick_linux.get_current_username()
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_32', username=username)
    >>> path_gecko_32_filename = get_gecko_32_filename_from_appwiz(wine_prefix, username)
    >>> assert str(path_gecko_32_filename).startswith('wine_gecko-') and str(path_gecko_32_filename).endswith('-x86.msi')
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_64', username=username)
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

    response = configmagick_linux.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | grep -F "wine_gecko-" | grep -F "-x86.msi"'
                                                    .format(path_appwiz=path_appwiz), shell=True, quiet=True)
    gecko_32_filename = response.stdout
    if not gecko_32_filename:
        raise RuntimeError('can not determine Gecko 32 Bit MSI File Name for WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    path_gecko_32_filename = pathlib.Path(gecko_32_filename)
    return path_gecko_32_filename


def get_gecko_64_filename_from_appwiz(wine_prefix: Union[str, pathlib.Path], username: str) -> pathlib.Path:
    """
    Gecko 64 Bit Filename can only be read from a 64 Bit Wine Prefix

    >>> import unittest
    >>> wine_install.install_wine(wine_release='staging')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    OK
    ...
    >>> wine_machine_install.install_wine_machine(wine_prefix='wine_test_32',wine_arch='win32',\
                                                  overwrite_existing_wine_machine=True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Using winetricks ...

    >>> wine_machine_install.install_wine_machine(wine_prefix='wine_test_64',wine_arch='win64',\
                                                  overwrite_existing_wine_machine=True)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ---...
    You are using a 64-bit WINEPREFIX. ...


    >>> username = configmagick_linux.get_current_username()
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_32', username=username)
    >>> unittest.TestCase().assertRaises(RuntimeError, get_gecko_64_filename_from_appwiz, wine_prefix, username)

    >>> wine_prefix = lib_wine.get_and_check_wine_prefix('wine_test_64', username=username)
    >>> path_gecko_64_filename = get_gecko_64_filename_from_appwiz(wine_prefix, username)
    >>> assert str(path_gecko_64_filename).startswith('wine_gecko-') and str(path_gecko_64_filename).endswith('-x86_64.msi')

    """
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    if wine_arch == 'win32':
        raise RuntimeError('can not determine Gecko 64 Bit msi Filename from a 32 Bit Wine Machine')
    else:
        path_appwiz = pathlib.Path(wine_prefix) / 'drive_c/windows/system32/appwiz.cpl'

    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Gecko MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))

    response = configmagick_linux.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | grep -F "wine_gecko-" | grep -F "-x86_64.msi"'
                                                    .format(path_appwiz=path_appwiz), shell=True, quiet=True)
    gecko_64_filename = response.stdout
    if not gecko_64_filename:
        raise RuntimeError('can not determine Gecko 64 Bit MSI File Name for WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    path_gecko_64_filename = pathlib.Path(gecko_64_filename)
    return path_gecko_64_filename
