# ### STDLIB
import subprocess

# ### OWN
import configmagick_linux
import lib_log_utils


def install_wine(wine_release: str, linux_release_name: str = configmagick_linux.get_linux_release_name()) -> None:
    """installs wine. syntax: install_wine --wine_release=(stable|devel|staging)

    Args:
        --wine_release=stable: this is the current stable wine version (probably the one you should install)
        --wine_release=devel: this package is used to provide development headers, mostly used by third party software compilation.
        --wine_release=staging: this is the most recent testing wine version

    """

    lib_log_utils.banner_verbose('Installing WINE and WINETRICKS: \n'
                                 'linux_release_name = "{linux_release_name}" \n'
                                 'wine_release = "{wine_release}" \n'
                                 .format(linux_release_name=linux_release_name, wine_release=wine_release)
                                 )
    raise_if_wine_release_unknown(wine_release)
    add_architecture_386()
    add_wine_key(linux_release_name=linux_release_name)
    install_libfaudio0_if_needed()
    update_wine_packages()
    install_wine_packages(wine_release)
    install_winetricks()


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


def add_architecture_386() -> None:
    lib_log_utils.log_debug('Add 386 Architecture')
    configmagick_linux.run_shell_command('dpkg --add-architecture i386')


def add_wine_key(linux_release_name: str) -> None:
    """
    >>> # add_wine_key(configmagick_linux.get_linux_release_name())

    """
    lib_log_utils.log_debug('Add Wine Key and Repository, linux_release_name="linux_release_name"'
                            .format(linux_release_name=linux_release_name))
    configmagick_linux.run_shell_command('rm -f ./winehq.key*', shell=True)
    configmagick_linux.run_shell_command('wget -nv -c https://dl.winehq.org/wine-builds/winehq.key')
    configmagick_linux.run_shell_command('apt-key add winehq.key')
    configmagick_linux.run_shell_command('rm -f ./winehq.key*', shell=True)
    configmagick_linux.run_shell_command('apt-add-repository "deb https://dl.winehq.org/wine-builds/ubuntu/ {linux_release_name} main"'
                                         .format(linux_release_name=linux_release_name))


def install_libfaudio0_if_needed() -> None:
    if int(configmagick_linux.get_linux_release_number_major()) > 18:
        try:
            lib_log_utils.log_debug('Install libfaudio0')
            configmagick_linux.install_linux_package('libfaudio0')
        except subprocess.CalledProcessError:
            lib_log_utils.log_debug('Install libfaudio0 backport')
            install_libfaudio0_backport()


def install_libfaudio0_backport() -> None:
    configmagick_linux.run_shell_command('add-apt-repository ppa:cybermax-dexter/sdl2-backport -y')


def update_wine_packages() -> None:
    lib_log_utils.log_debug('Update wine packages')
    configmagick_linux.update()


def install_wine_packages(wine_release: str, reinstall: bool = False) -> None:
    configmagick_linux.install_linux_package('winehq-{wine_release}'.format(wine_release=wine_release),
                                             parameters=['--install-recommends'], reinstall=reinstall)
    configmagick_linux.install_linux_packages(['cabextract', 'libxml2', 'libpng-dev'], reinstall=reinstall)
    lib_log_utils.banner_success('Wine Release "{wine_release}" Version "{wine_version_number}" installed on linux "{linux_release_name}"'
                                 .format(wine_release=wine_release,
                                         wine_version_number=get_wine_version_number(),
                                         linux_release_name=configmagick_linux.get_linux_release_name())
                                 )


def get_wine_version_number() -> str:
    wine_version_number = configmagick_linux.run_shell_command('wine --version', quiet=True).stdout
    return str(wine_version_number)


def install_winetricks() -> None:
    lib_log_utils.log_debug('Install Winetricks')
    configmagick_linux.run_shell_command('rm -f /usr/bin/winetricks')
    configmagick_linux.run_shell_command(
        'wget -nv -c --directory-prefix=/usr/bin/ https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks')
    configmagick_linux.run_shell_command('chmod +x /usr/bin/winetricks')


def update_winetricks() -> None:
    lib_log_utils.log_debug('Update Winetricks')
    configmagick_linux.run_shell_command('winetricks -q --self-update')
