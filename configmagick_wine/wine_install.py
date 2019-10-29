# ### STDLIB
import subprocess

# ### OWN
import configmagick_linux
import lib_log_utils
import lib_shell


def install_wine(wine_release: str, linux_release_name: str = configmagick_linux.get_linux_release_name(), quiet: bool = False) -> None:
    """installs wine. syntax: install_wine --wine_release=(stable|devel|staging)

    Args:
        --wine_release=stable: this is the current stable wine version (probably the one you should install)
        --wine_release=devel: this package is used to provide development headers, mostly used by third party software compilation.
        --wine_release=staging: this is the most recent testing wine version

    """

    lib_log_utils.banner_verbose('Installing WINE: \n'
                                 'linux_release_name = "{linux_release_name}" \n'
                                 'wine_release = "{wine_release}" \n'
                                 .format(linux_release_name=linux_release_name, wine_release=wine_release), quiet=quiet)

    raise_if_wine_release_unknown(wine_release)
    add_architecture_386(quiet=quiet)
    add_wine_key(linux_release_name=linux_release_name, quiet=quiet)
    install_libfaudio0_if_needed(quiet=quiet)
    update_wine_packages(quiet=quiet)
    install_wine_packages(wine_release, quiet=quiet)

    lib_log_utils.banner_success('Wine Installation OK - Wine Release: "{wine_release}", Wine Version: "{wine_version_number}"'
                                 .format(wine_release=wine_release, wine_version_number=get_wine_version_number()), quiet=quiet)


def raise_if_wine_release_unknown(wine_release: str) -> None:
    """
    >>> import unittest
    >>> raise_if_wine_release_unknown('stable')
    >>> raise_if_wine_release_unknown('devel')
    >>> raise_if_wine_release_unknown('staging')
    >>> unittest.TestCase().assertRaises(RuntimeError, raise_if_wine_release_unknown, 'unknown')

    """
    l_wine_releases = ['stable', 'devel', 'staging']
    if wine_release not in l_wine_releases:
        msg = 'Wine release "{wine_release}" is not a valid wine release ("stable", "devel", "staging")'.format(wine_release=wine_release)
        lib_log_utils.banner_error(msg)
        raise RuntimeError(msg)


def add_architecture_386(quiet: bool = False) -> None:
    lib_log_utils.log_verbose('Add 386 Architecture', quiet=quiet)
    lib_shell.run_shell_command('dpkg --add-architecture i386', use_sudo=True, pass_stdout_stderr_to_sys=True, quiet=quiet)


def add_wine_key(linux_release_name: str, quiet: bool = False) -> None:
    """
    >>> add_wine_key(configmagick_linux.get_linux_release_name(), quiet=True)

    """
    lib_log_utils.log_verbose('Add Wine Key and Repository, linux_release_name="{linux_release_name}"'
                              .format(linux_release_name=linux_release_name), quiet=quiet)
    lib_shell.run_shell_command('rm -f ./winehq.key*', shell=True, use_sudo=True, quiet=quiet)
    lib_shell.run_shell_command('wget -nv -c https://dl.winehq.org/wine-builds/winehq.key', use_sudo=True, quiet=quiet)
    lib_shell.run_shell_command('apt-key add winehq.key', use_sudo=True, quiet=quiet)
    lib_shell.run_shell_command('rm -f ./winehq.key*', shell=True, use_sudo=True, quiet=quiet)
    lib_shell.run_shell_command('apt-add-repository "deb https://dl.winehq.org/wine-builds/ubuntu/ {linux_release_name} main"'
                                .format(linux_release_name=linux_release_name),
                                use_sudo=True, pass_stdout_stderr_to_sys=True, quiet=quiet)


def install_libfaudio0_if_needed(quiet: bool = False) -> None:
    if int(configmagick_linux.get_linux_release_number_major()) > 18:
        try:
            lib_log_utils.log_verbose('Install libfaudio0', quiet=quiet)
            configmagick_linux.install_linux_package('libfaudio0', quiet=quiet)
        except subprocess.CalledProcessError:
            lib_log_utils.log_verbose('Install libfaudio0 backport', quiet=quiet)
            install_libfaudio0_backport(quiet=quiet)


def install_libfaudio0_backport(quiet: bool = False) -> None:
    lib_shell.run_shell_command('add-apt-repository ppa:cybermax-dexter/sdl2-backport -y', use_sudo=True, quiet=quiet)


def update_wine_packages(quiet: bool = False) -> None:
    lib_log_utils.log_verbose('Update wine packages', quiet=quiet)
    configmagick_linux.full_update_and_upgrade(quiet=quiet)


def install_wine_packages(wine_release: str, reinstall: bool = False, quiet: bool = False) -> None:
    lib_log_utils.log_verbose('Install Wine Packages', quiet=quiet)
    configmagick_linux.install_linux_package('winehq-{wine_release}'.format(wine_release=wine_release),
                                             parameters=['--install-recommends'], reinstall=reinstall, quiet=quiet)
    configmagick_linux.install_linux_packages(['cabextract', 'libxml2', 'libpng-dev'], reinstall=reinstall, quiet=quiet)


def get_wine_version_number() -> str:
    wine_version_number = lib_shell.run_shell_command('wine --version', quiet=True).stdout
    return str(wine_version_number)


def install_winetricks(quiet: bool = False) -> None:
    lib_log_utils.banner_verbose('Installing Winetricks', quiet=quiet)
    lib_shell.run_shell_command('rm -f /usr/bin/winetricks', use_sudo=True, quiet=quiet)
    lib_shell.run_shell_command('wget -nv -c --directory-prefix=/usr/bin/ https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks',
                                use_sudo=True, quiet=quiet)
    lib_shell.run_shell_command('chmod +x /usr/bin/winetricks', use_sudo=True, quiet=quiet)
    lib_log_utils.banner_success('Winetricks Installation OK', quiet=quiet)


def update_winetricks(quiet: bool = False) -> None:
    lib_log_utils.banner_verbose('Updating Winetricks', quiet=quiet)
    lib_shell.run_shell_command('winetricks -q --self-update', use_sudo=True, quiet=quiet)
    lib_log_utils.banner_success('Winetricks Update OK', quiet=quiet)


def is_wine_installed() -> bool:
    """
    >>> if not is_wine_installed():
    ...     install_wine(wine_release='staging', quiet=True)
    >>> assert is_wine_installed() == True

    """

    # noinspection PyBroadException
    try:
        get_wine_version_number()
        return True
    except Exception:
        return False
