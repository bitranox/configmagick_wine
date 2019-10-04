# ### STDLIB
import logging

# ### OWN
import configmagick_linux
import lib_log_utils


def install_wine(wine_release: str, linux_release_name: str = configmagick_linux.get_linux_release_name()) -> None:

    lib_log_utils.banner_verbose('Installing WINE and WINETRICKS: \n'
                                 'linux_release_name = {linux_release_name} \n'
                                 'wine_release = {wine_release} \n'
                                 .format(linux_release_name='x', wine_release=wine_release)
                                 )
    raise_if_wine_release_unknown(wine_release)
    add_architecture_386()
    add_wine_key(linux_release_name=linux_release_name)


def add_architecture_386() -> None:
    lib_log_utils.log_debug('add 386 Architecture')
    configmagick_linux.run_shell_command('dpkg --add-architecture i386')


def add_wine_key(linux_release_name: str) -> None:
    """
    >>> add_wine_key(configmagick_linux.get_linux_release_name())

    """
    lib_log_utils.log_debug('add Wine Key and Repository, linux_release_name="linux_release_name"'
                            .format(linux_release_name=linux_release_name))
    configmagick_linux.run_shell_command('rm -f ./winehq.key*', shell=True)
    configmagick_linux.run_shell_command('wget -nv -c https://dl.winehq.org/wine-builds/winehq.key')
    configmagick_linux.run_shell_command('apt-key add winehq.key')
    configmagick_linux.run_shell_command('rm -f ./winehq.key*')
    configmagick_linux.run_shell_command('apt-add-repository "deb https://dl.winehq.org/wine-builds/ubuntu/ {linux_release_name} main"'
                                         .format(linux_release_name=linux_release_name))


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
