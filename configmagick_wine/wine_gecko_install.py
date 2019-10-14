# ### STDLIB
import pathlib
import time
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
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    # TODO
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def get_gecko_32_filename_from_appwiz(wine_prefix: pathlib.Path, username: str) -> pathlib.Path:
    """
    >>> # wine_install.install_wine(wine_release='staging')
    >>> # wine_prefix = configmagick_linux.get_path_home_dir_current_user() / '.wine'
    >>> # username = configmagick_linux.get_current_username()
    >>> username = 'consul'
    >>> wine_prefix = pathlib.Path('home/consul/wine_test_32')
    >>> get_gecko_32_filename_from_appwiz(wine_prefix, username)
    >>> wine_prefix = pathlib.Path('home/consul/wine_test_64')
    >>> get_gecko_32_filename_from_appwiz(wine_prefix, username)


    """
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    if wine_arch == 'win32':
        path_appwiz = wine_prefix / 'drive_c/windows/system32/appwiz.cpl'
    else:
        path_appwiz = wine_prefix / 'drive_c/windows/syswow64/appwiz.cpl'

    gecko_32_filename = configmagick_linux.run_shell_command('strings -d --bytes=12 --encoding=s "{path_appwiz}" | grep wine_gecko | grep .msi'
                                                             .format(path_appwiz=path_appwiz), shell=True, quiet=True)
    if not gecko_32_filename:
        raise RuntimeError('can not determine Gecko 32 Bit MSI File Name for WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    return pathlib.Path(str(gecko_32_filename))



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
