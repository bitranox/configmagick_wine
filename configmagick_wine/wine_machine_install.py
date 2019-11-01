# ### STDLIB
import pathlib
from typing import Union

# ### OWN
import configmagick_linux
import lib_log_utils
import lib_shell


# ####### PROJ
try:
    # imports for local pytest
    from . import lib_wine             # type: ignore # pragma: no cover
    from . import wine_install         # type: ignore # pragma: no cover
except ImportError:                    # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                    # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_install                # type: ignore # pragma: no cover


def install_wine_machine(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                         wine_arch: str = 'win32',
                         username: str = configmagick_linux.get_current_username(),
                         overwrite_existing_wine_machine: bool = False,
                         quiet: bool = False) -> None:
    """installs wine. syntax: install_wine --wine_release=(stable|devel|staging)

    Args:
        --wine_prefix=<prefix>                  --> /home/username/<prefix> or
        --wine_prefix=/home/username/<prefix>   --> /home/username/<prefix>
        --overwrite_existing_wine_machine

    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    wine_arch = lib_wine.get_and_check_wine_arch_valid(wine_arch=wine_arch)

    lib_log_utils.banner_verbose('Installing Wine Machine:\n'
                                 'wine_prefix = "{wine_prefix}"\n'
                                 'wine_arch = "{wine_arch}"\n'
                                 'username = "{username}"\n'
                                 'overwrite_existing_wine_machine = {overwrite_existing_wine_machine}\n'
                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         username=username,
                                         overwrite_existing_wine_machine=overwrite_existing_wine_machine),
                                 quiet=quiet)

    lib_wine.raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix=wine_prefix, username=username)
    delete_existing_wine_machine_or_raise(overwrite_existing_wine_machine=overwrite_existing_wine_machine,
                                          wine_prefix=wine_prefix, username=username)
    create_wine_machine(wine_prefix=wine_prefix, username=username, wine_arch=wine_arch, quiet=quiet)
    lib_log_utils.banner_success('Wine Machine creation OK')


def disable_gui_crash_dialogs(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                              username: str = configmagick_linux.get_current_username(),
                              quiet: bool = False) -> None:
    """
    >>> create_wine_test_prefixes()
    >>> disable_gui_crash_dialogs(wine_prefix='wine_test_32', quiet=True)
    >>> disable_gui_crash_dialogs(wine_prefix='wine_test_64', quiet=True)

    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    lib_log_utils.banner_verbose('Disable GUI Crash Dialogs on WINEPREFIX="{wine_prefix}", WINEARCH="{wine_arch}"'
                                 .format(wine_prefix=wine_prefix, wine_arch=wine_arch), quiet=quiet)
    lib_shell.run_shell_command('WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" winetricks nocrashdialog'
                                .format(wine_prefix=wine_prefix, wine_arch=wine_arch),
                                run_as_user=username, shell=True, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case
    lib_log_utils.banner_success('GUI Crash Dialogs disabled')


def set_windows_version(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                        username: str = configmagick_linux.get_current_username(),
                        windows_version: str = 'win7',
                        quiet: bool = False) -> None:
    """
    >>> create_wine_test_prefixes()
    >>> set_windows_version(wine_prefix='wine_test_32', windows_version='win10', quiet=True)
    >>> set_windows_version(wine_prefix='wine_test_64', windows_version='win10', quiet=True)
    >>> set_windows_version(wine_prefix='wine_test_32', windows_version='win7', quiet=True)
    >>> set_windows_version(wine_prefix='wine_test_64', windows_version='win7', quiet=True)

    """

    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    windows_version = lib_wine.get_windows_version(windows_version=windows_version)
    lib_log_utils.banner_verbose('Set Windows Version on "{wine_prefix}" to "{windows_version}"'
                                 .format(wine_prefix=wine_prefix, windows_version=windows_version),
                                 quiet=quiet)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    lib_shell.run_shell_command('WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" winetricks -q "{windows_version}"'
                                .format(wine_prefix=wine_prefix, wine_arch=wine_arch, windows_version=windows_version),
                                run_as_user=username, shell=True, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case
    lib_log_utils.banner_success('Windows version Set to "{windows_version}"'.format(windows_version=windows_version))


def create_wine_machine(wine_prefix: pathlib.Path,
                        username: str,
                        wine_arch: str = 'win32',
                        quiet: bool = False) -> None:

    lib_log_utils.log_verbose('Create Wine Machine: WINEPREFIX={wine_prefix}, WINEARCH={wine_arch}'
                              .format(wine_prefix=wine_prefix, wine_arch=wine_arch),
                              quiet=quiet)
    lib_shell.run_shell_command('mkdir -p {wine_prefix}'.format(wine_prefix=wine_prefix), use_sudo=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)
    # we really set DISPLAY to an empty value, otherwise Errors under XVFB
    lib_shell.run_shell_command('DISPLAY="" WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" winecfg'
                                .format(wine_prefix=wine_prefix, wine_arch=wine_arch),
                                shell=True, run_as_user=username,
                                pass_stdout_stderr_to_sys=True,
                                quiet=quiet)
    configmagick_linux.wait_for_file_to_be_created(filename=wine_prefix / 'system.reg')
    configmagick_linux.wait_for_file_to_be_unchanged(filename=wine_prefix / 'system.reg')
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)


def delete_existing_wine_machine_or_raise(overwrite_existing_wine_machine: bool, wine_prefix: Union[str, pathlib.Path],
                                          username: str = configmagick_linux.get_current_username()) -> None:
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    lib_wine.raise_if_path_outside_homedir(wine_prefix, username=username)
    if wine_prefix.exists():
        if overwrite_existing_wine_machine:
            lib_log_utils.banner_warning('deleting old Wine Machine "{wine_prefix}"'.format(wine_prefix=wine_prefix))
            lib_shell.run_shell_command('rm -Rf "{wine_prefix}"'.format(wine_prefix=wine_prefix), shell=True, quiet=True, use_sudo=True)
            if wine_prefix.exists():
                raise RuntimeError('the WINEPREFIX can not be deleted: "{wine_prefix}"'.format(wine_prefix=wine_prefix))
        else:
            raise RuntimeError('the WINEPREFIX does already exist, and overwrite is disabled: "{wine_prefix}"'.format(wine_prefix=wine_prefix))


def create_wine_test_prefixes() -> None:
    """
    >>> create_wine_test_prefixes()

    """

    if not wine_install.is_wine_installed():
        wine_install.install_wine(wine_release='staging', quiet=True)
        wine_install.install_winetricks(quiet=True)
        wine_install.update_winetricks(quiet=True)

    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix='wine_test_32', username=configmagick_linux.get_current_username())
    if not wine_prefix.exists():
        install_wine_machine(wine_prefix='wine_test_32', wine_arch='win32', quiet=True)
        disable_gui_crash_dialogs(wine_prefix='wine_test_32', quiet=True)
        set_windows_version(windows_version='win7', wine_prefix='wine_test_32', quiet=True)

    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix='wine_test_64', username=configmagick_linux.get_current_username())
    if not wine_prefix.exists():
        install_wine_machine(wine_prefix='wine_test_64', wine_arch='win64', quiet=True)
        disable_gui_crash_dialogs(wine_prefix='wine_test_64', quiet=True)
        set_windows_version(windows_version='win7', wine_prefix='wine_test_64', quiet=True)
