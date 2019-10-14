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
    from . import wine_gecko_install   # type: ignore # pragma: no cover
    from . import wine_install         # type: ignore # pragma: no cover
    from . import wine_mono_install    # type: ignore # pragma: no cover
except ImportError:                    # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                    # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_gecko_install          # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_install                # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_mono_install           # type: ignore # pragma: no cover


def install_wine_machine(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                         wine_arch: str = 'win32',
                         windows_version: str = 'win7',
                         username: str = configmagick_linux.get_current_username(),
                         overwrite_existing_wine_machine: bool = False,
                         install_mono: bool = True,
                         install_gecko: bool = True
                         ) -> None:
    """installs wine. syntax: install_wine --wine_release=(stable|devel|staging)

    Args:
        --wine_prefix=<prefix>                  --> /home/username/<prefix> or
        --wine_prefix=/home/username/<prefix>   --> /home/username/<prefix>
        --overwrite_existing_wine_machine

    >>> wine_install.install_wine(wine_release='staging')
    >>> install_wine_machine(wine_prefix='wine_test_32', \
        wine_arch='win32', overwrite_existing_wine_machine=True, install_mono=False, install_gecko=False)   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Using winetricks ...
    >>> install_wine_machine(wine_prefix='wine_test_32', \
        wine_arch='win32', overwrite_existing_wine_machine=False, install_mono=False, install_gecko=False)   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    RuntimeError: the WINEPREFIX does already exist, and overwrite is disabled: ...


    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    wine_arch = lib_wine.get_wine_arch(wine_arch=wine_arch)
    windows_version = lib_wine.get_windows_version(windows_version=windows_version)

    lib_log_utils.banner_verbose('Installing Wine Machine:\n'
                                 'wine_prefix = "{wine_prefix}"\n'
                                 'wine_arch = "{wine_arch}"\n'
                                 'windows_version = "{windows_version}"\n'
                                 'username = "{username}"\n'
                                 'overwrite_existing_wine_machine = {overwrite_existing_wine_machine}\n'
                                 'Install Mono = {install_mono}\n'
                                 'Install Gecko = {install_gecko}\n'

                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         windows_version=windows_version,
                                         username=username,
                                         overwrite_existing_wine_machine=overwrite_existing_wine_machine,
                                         install_mono=install_mono,
                                         install_gecko=install_gecko)
                                 )

    lib_wine.raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix=wine_prefix, username=username)
    delete_existing_wine_machine_or_raise(overwrite_existing_wine_machine, wine_prefix)
    create_wine_machine(wine_prefix=wine_prefix, username=username, wine_arch=wine_arch, windows_version=windows_version)
    disable_gui_crash_dialogs(wine_prefix=wine_prefix, username=username)

    if install_mono:
        wine_mono_install.install_wine_mono(wine_prefix=wine_prefix, username=username)
    if install_gecko:
        wine_gecko_install.install_wine_gecko(wine_prefix=wine_prefix, username=username)

    set_windows_version(wine_prefix=wine_prefix, username=username, windows_version=windows_version)


def disable_gui_crash_dialogs(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                              username: str = configmagick_linux.get_current_username()) -> None:
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    lib_log_utils.log_verbose('Disable GUI Crash Dialogs on WINEPREFIX="{wine_prefix}", WINEARCH="{wine_arch}"'
                              .format(wine_prefix=wine_prefix, wine_arch=wine_arch))
    configmagick_linux.run_shell_command('runuser -l {username} -c \'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" winetricks nocrashdialog\''
                                         .format(username=username, wine_prefix=wine_prefix, wine_arch=wine_arch))
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def set_windows_version(wine_prefix: Union[str, pathlib.Path], username: str, windows_version: str) -> None:
    lib_log_utils.log_verbose('Set Windows Version on "{wine_prefix}" to "{windows_version}"'
                              .format(wine_prefix=wine_prefix, windows_version=windows_version))
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    configmagick_linux.run_shell_command('runuser -l {username} -c \'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" winetricks -q "{windows_version}"\''
                                         .format(username=username, wine_prefix=wine_prefix, wine_arch=wine_arch, windows_version=windows_version))
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case


def create_wine_machine(wine_prefix: pathlib.Path,
                        username: str,
                        wine_arch: str = 'win32',
                        windows_version: str = 'win7') -> None:

    lib_log_utils.log_verbose('Create Wine Machine: WINEPREFIX={wine_prefix}, WINEARCH={wine_arch}, windows_version={windows_version}'
                              .format(wine_prefix=wine_prefix,
                                      wine_arch=wine_arch,
                                      windows_version=windows_version,))
    configmagick_linux.run_shell_command('mkdir -p {wine_prefix}'.format(wine_prefix=wine_prefix))
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)
    # we really set DISPLAY to an empty value, otherwise Errors under XVFB
    configmagick_linux.run_shell_command('runuser -l {username} -c \'DISPLAY="" WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" winecfg\''
                                         .format(username=username, wine_prefix=wine_prefix, wine_arch=wine_arch), shell=True)
    configmagick_linux.wait_for_file_to_be_created(filename=wine_prefix / 'system.reg')
    configmagick_linux.wait_for_file_to_be_unchanged(filename=wine_prefix / 'system.reg')
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)


def delete_existing_wine_machine_or_raise(overwrite_existing_wine_machine: bool, wine_prefix: Union[str, pathlib.Path]) -> None:
    wine_prefix = pathlib.Path(wine_prefix)                 # if wine_prefix is passed as string
    lib_wine.raise_if_path_outside_homedir(wine_prefix)
    if wine_prefix.exists():
        if overwrite_existing_wine_machine:
            lib_log_utils.banner_warning('deleting old Wine Machine "{wine_prefix}"'.format(wine_prefix=wine_prefix))
            configmagick_linux.run_shell_command('rm -Rf "${wine_prefix}"'.format(wine_prefix=wine_prefix))
        else:
            raise RuntimeError('the WINEPREFIX does already exist, and overwrite is disabled: "{wine_prefix}"'.format(wine_prefix=wine_prefix))
