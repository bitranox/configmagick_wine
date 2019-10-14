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
        path_appwiz = wine_prefix / 'drive_c/windows/system32/appwiz.cpl'
    else:
        path_appwiz = wine_prefix / 'drive_c/windows/syswow64/appwiz.cpl'

    if not path_appwiz.is_file():
        raise RuntimeError('can not determine Gecko MSI Filename, File "{path_appwiz}" does not exist'.format(path_appwiz=path_appwiz))

    response = configmagick_linux.run_shell_command('strings -d --bytes=12 "{path_appwiz}" | grep wine_gecko | grep .msi'
                                                    .format(path_appwiz=path_appwiz), shell=True, quiet=True)
    gecko_32_filename = response.stdout
    if not gecko_32_filename:
        raise RuntimeError('can not determine Gecko 32 Bit MSI File Name for WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    path_gecko_32_filename = pathlib.Path(gecko_32_filename)
    return path_gecko_32_filename
