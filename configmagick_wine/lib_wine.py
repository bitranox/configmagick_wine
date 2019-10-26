# ### STDLIB
import pathlib
from typing import Union

# ### OWN
import configmagick_linux
import lib_regexp
import lib_shell


def fix_wine_permissions(wine_prefix: Union[str, pathlib.Path], username: str) -> None:
    wine_prefix = get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed

    if wine_prefix.exists():
        lib_shell.run_shell_command('chown -R "{username}"."{username}" "{wine_prefix}"'
                                    .format(username=username, wine_prefix=wine_prefix),
                                    quiet=True, use_sudo=True)
        lib_shell.run_shell_command('chmod -R 0775 "{wine_prefix}"'
                                    .format(wine_prefix=wine_prefix),
                                    quiet=True, use_sudo=True)
    fix_permissions_winecache(username=username)


def get_and_check_wine_prefix(wine_prefix: Union[str, pathlib.Path], username: str) -> pathlib.Path:
    """
    if wine_prefix does not start with /home/ then prepend /home/<username>/

    >>> assert get_and_check_wine_prefix(wine_prefix='/home/test/my_wine', username='test') == pathlib.PosixPath('/home/test/my_wine')
    >>> assert get_and_check_wine_prefix(wine_prefix='my_wine', username='test') == pathlib.PosixPath('/home/test/my_wine')

    """
    wine_prefix = pathlib.Path(wine_prefix)                 # if wine_prefix is passed as string
    if not str(wine_prefix).startswith('/home/'):
        wine_prefix = pathlib.Path('/home/{username}'.format(username=username)) / str(wine_prefix)
    raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix=wine_prefix, username=username)
    return wine_prefix


def get_and_check_wine_arch_valid(wine_arch: str = '') -> str:
    """
    check for valid winearch - if wine_arch is empty, default to win32
    valid choices: win32, win64

    >>> import unittest
    >>> assert get_and_check_wine_arch_valid() == 'win32'
    >>> assert get_and_check_wine_arch_valid('win32') == 'win32'
    >>> assert get_and_check_wine_arch_valid('win64') == 'win64'
    >>> unittest.TestCase().assertRaises(RuntimeError, get_and_check_wine_arch_valid, wine_arch='invalid')
    """
    valid_wine_archs = ['win32', 'win64']
    if not wine_arch:
        wine_arch = 'win32'
    wine_arch = wine_arch.lower().strip()
    if wine_arch not in valid_wine_archs:
        raise RuntimeError('Invalid wine_arch: "{wine_arch}"'.format(wine_arch=wine_arch))
    return wine_arch


def get_windows_version(windows_version: str = 'win7') -> str:
    """
    valid windows versions : 'nt40', 'vista', 'win10', 'win2k', 'win2k3', 'win2k8', 'win31', 'win7', 'win8', 'win81', 'win95', 'win98', 'winxp'

    >>> import unittest
    >>> assert get_windows_version() == 'win7'
    >>> assert get_windows_version('nt40') == 'nt40'
    >>> unittest.TestCase().assertRaises(RuntimeError, get_windows_version, windows_version='invalid')
    """
    valid_windows_versions = ['nt40', 'vista', 'win10', 'win2k', 'win2k3', 'win2k8', 'win31', 'win7', 'win8', 'win81', 'win95', 'win98', 'winxp']
    if not windows_version:
        windows_version = 'win7'
    windows_version = windows_version.lower().strip()
    if windows_version not in valid_windows_versions:
        raise RuntimeError('Invalid windows_version: "{windows_version}"'.format(windows_version=windows_version))
    return windows_version


def get_path_wine_cache_for_user(username: str) -> pathlib.Path:
    path_user_home = configmagick_linux.get_path_home_dir_user(username=username)
    path_wine_cache = path_user_home / '.cache/wine'
    return pathlib.Path(path_wine_cache)


def create_wine_cache_for_user(username: str) -> None:
    path_wine_cache = get_path_wine_cache_for_user(username=username)
    if not path_wine_cache.is_dir():
        lib_shell.run_shell_command('mkdir -p {path_wine_cache}'.format(path_wine_cache=path_wine_cache),
                                    quiet=True, use_sudo=True)
    fix_permissions_winecache(username=username)


def fix_permissions_winecache(username: str) -> None:
    path_wine_cache = get_path_wine_cache_for_user(username=username)
    if path_wine_cache.exists():
        lib_shell.run_shell_command('chown -R "{username}"."{username}" "{path_wine_cache}"'
                                    .format(username=username, path_wine_cache=path_wine_cache),
                                    quiet=True, use_sudo=True)
        lib_shell.run_shell_command('chmod -R 0775 "{path_wine_cache}"'
                                    .format(path_wine_cache=path_wine_cache),
                                    quiet=True, use_sudo=True)


def get_wine_arch_from_wine_prefix(wine_prefix: Union[str, pathlib.Path], username: str) -> str:
    l_valid_wine_archs = ['win32', 'win64']
    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    path_wine_system_registry = get_and_check_path_wine_system_registry(wine_prefix=wine_prefix)
    with open(str(path_wine_system_registry), mode='r') as registry_file:
        registry_file_content = registry_file.read()
        l_result = lib_regexp.reg_grep('#arch=', registry_file_content)
    if not l_result:
        raise RuntimeError('can not get wine_arch from system_registry="{path_wine_system_registry}"'
                           .format(path_wine_system_registry=path_wine_system_registry))
    wine_arch = l_result[0].rsplit('=', 1)[1].strip().lower()
    if wine_arch not in l_valid_wine_archs:
        raise RuntimeError('invalid wine_arch detected in system_registry="{path_wine_system_registry}": "{wine_arch}"'
                           .format(path_wine_system_registry=path_wine_system_registry, wine_arch=wine_arch))
    return str(wine_arch)


def get_path_wine_system_registry(wine_prefix: pathlib.Path) -> pathlib.Path:
    path_wine_system_registry = wine_prefix / 'system.reg'
    return path_wine_system_registry


def get_and_check_path_wine_system_registry(wine_prefix: pathlib.Path) -> pathlib.Path:
    path_wine_system_registry = get_path_wine_system_registry(wine_prefix=wine_prefix)
    if not path_wine_system_registry.exists():
        raise RuntimeError('can not find system_registry for WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    return path_wine_system_registry


def raise_if_path_outside_homedir(wine_prefix: Union[str, pathlib.Path]) -> None:
    """
    >>> import unittest
    >>> assert raise_if_path_outside_homedir(wine_prefix='/home/test') is None
    >>> unittest.TestCase().assertRaises(RuntimeError, raise_if_path_outside_homedir, wine_prefix='/test')

    """
    wine_prefix = pathlib.Path(wine_prefix)                 # if wine_prefix is passed as string
    if not str(wine_prefix).startswith('/home/'):
        raise RuntimeError('the WINEPREFIX does not reside under /HOME: "{wine_prefix}"'.format(wine_prefix=wine_prefix))


def raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix: Union[str, pathlib.Path], username: str) -> None:
    """
    >>> import unittest
    >>> assert raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix='/home/test/wine', username='test') is None
    >>> unittest.TestCase().assertRaises(RuntimeError, raise_if_wine_prefix_does_not_match_user_homedir, wine_prefix='/home/test/wine', username='xxx')

    """
    if not str(wine_prefix).startswith('/home/{username}/'.format(username=username)):
        raise RuntimeError('wine_prefix "{wine_prefix}" is not within user home directory "/home/{username}"'.format(
            wine_prefix=wine_prefix, username=username))


def is_file_in_wine_cache(username: str, filename: pathlib.Path) -> bool:
    path_wine_cache = get_path_wine_cache_for_user(username=username)
    path_file = path_wine_cache / filename
    if path_file.is_file():
        return True
    else:
        return False


def download_file_to_winecache(download_link: str, filename: pathlib.Path, username: str) -> None:
    """
    >>> download_link = 'https://source.winehq.org/winemono.php?v=4.9.3'
    >>> filename = pathlib.Path('wine-mono-4.9.3.msi')
    >>> username = configmagick_linux.get_current_username()
    >>> download_file_to_winecache(download_link=download_link, filename=filename, username=username)
    >>> assert pathlib.Path( configmagick_linux.get_path_home_dir_current_user() / '.cache/wine/wine-mono-4.9.3.msi').is_file()

    """
    create_wine_cache_for_user(username=username)
    path_wine_cache = get_path_wine_cache_for_user(username=username)
    download_filename = path_wine_cache / filename
    configmagick_linux.download_file(download_link=download_link, filename=download_filename)
    fix_permissions_winecache(username=username)


def remove_file_from_winecache(filename: pathlib.Path, username: str) -> None:
    create_wine_cache_for_user(username=username)
    path_wine_cache_file = get_path_wine_cache_for_user(username=username) / filename
    if path_wine_cache_file.exists():
        lib_shell.run_shell_command('rm -f "{path_wine_cache_file}"'.format(path_wine_cache_file=path_wine_cache_file),
                                    quiet=True, use_sudo=True)
