# ### STDLIB
import pathlib
import subprocess
from typing import Tuple, Union

# ### OWN
import configmagick_linux
import lib_list
import lib_regexp
import lib_shell

# ####### PROJ
try:
    # imports for local pytest
    from . import install_wine_machine  # type: ignore # pragma: no cover
except ImportError:                     # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import install_wine_machine                 # type: ignore # pragma: no cover


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


def get_and_check_wine_prefix(wine_prefix: Union[str, pathlib.Path],
                              username: str = configmagick_linux.get_current_username()) -> pathlib.Path:
    """
    if wine_prefix does not start with /home/ then prepend /home/<username>/

    >>> assert get_and_check_wine_prefix(wine_prefix='/home/test/my_wine', username='test') == pathlib.PosixPath('/home/test/my_wine')
    >>> assert get_and_check_wine_prefix(wine_prefix='my_wine', username='test') == pathlib.PosixPath('/home/test/my_wine')

    """
    wine_prefix = pathlib.Path(wine_prefix)                 # if wine_prefix is passed as string
    if username == 'root':
        if not str(wine_prefix).startswith('/root/'):
            wine_prefix = pathlib.Path('/root') / str(wine_prefix)
    else:
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


def get_path_wine_cache_for_user(username: str = configmagick_linux.get_current_username()) -> pathlib.Path:
    path_user_home = configmagick_linux.get_path_home_dir_user(username=username)
    path_wine_cache = path_user_home / '.cache/wine'
    return pathlib.Path(path_wine_cache)


def create_wine_cache_for_user(username: str = configmagick_linux.get_current_username()) -> None:
    path_wine_cache = get_path_wine_cache_for_user(username=username)
    if not path_wine_cache.is_dir():
        lib_shell.run_shell_command('mkdir -p {path_wine_cache}'.format(path_wine_cache=path_wine_cache), quiet=True, use_sudo=True)
    fix_permissions_winecache(username=username)


def fix_permissions_winecache(username: str = configmagick_linux.get_current_username()) -> None:
    path_wine_cache = get_path_wine_cache_for_user(username=username)
    if path_wine_cache.exists():
        lib_shell.run_shell_command('chown -R "{username}"."{username}" "{path_wine_cache}"'
                                    .format(username=username, path_wine_cache=path_wine_cache),
                                    quiet=True, use_sudo=True)
        lib_shell.run_shell_command('chmod -R 0775 "{path_wine_cache}"'
                                    .format(path_wine_cache=path_wine_cache),
                                    quiet=True, use_sudo=True)


def get_wine_arch_from_wine_prefix(wine_prefix: Union[str, pathlib.Path],
                                   username: str = configmagick_linux.get_current_username()) -> str:
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
    """ get the path to wine system.reg
    """
    path_wine_system_registry = wine_prefix / 'system.reg'
    return path_wine_system_registry


def get_and_check_path_wine_system_registry(wine_prefix: pathlib.Path) -> pathlib.Path:
    path_wine_system_registry = get_path_wine_system_registry(wine_prefix=wine_prefix)
    if not path_wine_system_registry.exists():
        raise RuntimeError('can not find system_registry for WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    return path_wine_system_registry


def raise_if_path_outside_homedir(wine_prefix: Union[str, pathlib.Path],
                                  username: str = configmagick_linux.get_current_username()) -> None:
    """
    >>> import unittest
    >>> username = configmagick_linux.get_current_username()
    >>> path_user_home = configmagick_linux.get_path_home_dir_user(username=username)
    >>> assert raise_if_path_outside_homedir(wine_prefix=path_user_home / 'test', username=username) is None
    >>> unittest.TestCase().assertRaises(RuntimeError, raise_if_path_outside_homedir, wine_prefix='/test', username=username)

    """
    wine_prefix = pathlib.Path(wine_prefix)                 # if wine_prefix is passed as string
    path_user_home = configmagick_linux.get_path_home_dir_user(username=username)
    if not str(wine_prefix).startswith(str(path_user_home)):
        raise RuntimeError('the WINEPREFIX does not reside under {path_user_home}: "{wine_prefix}"'
                           .format(path_user_home=path_user_home, wine_prefix=wine_prefix))


def raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix: Union[str, pathlib.Path],
                                                     username: str = configmagick_linux.get_current_username()) -> None:
    """
    >>> import unittest
    >>> assert raise_if_wine_prefix_does_not_match_user_homedir(wine_prefix='/home/test/wine', username='test') is None
    >>> unittest.TestCase().assertRaises(RuntimeError, raise_if_wine_prefix_does_not_match_user_homedir, wine_prefix='/home/test/wine', username='xxx')

    """
    if username == 'root':
        if not str(wine_prefix).startswith('/root/'):
            raise RuntimeError('wine_prefix "{wine_prefix}" is not within user home directory "/root"'.format(wine_prefix=wine_prefix))
    else:
        if not str(wine_prefix).startswith('/home/{username}/'.format(username=username)):
            raise RuntimeError('wine_prefix "{wine_prefix}" is not within user home directory "/home/{username}"'.format(
                wine_prefix=wine_prefix, username=username))


def is_file_in_wine_cache(filename: pathlib.Path,
                          username: str = configmagick_linux.get_current_username()) -> bool:
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


def prepend_path_to_wine_registry_path(path_to_add: Union[str, pathlib.WindowsPath],
                                       wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                                       username: str = configmagick_linux.get_current_username()) -> None:
    """
    >>> install_wine_machine.create_wine_test_prefixes()
    >>> old_path = get_wine_registry_path(wine_prefix='wine_test_32')
    >>> prepend_path_to_wine_registry_path(path_to_add='c:\\\\test',wine_prefix='wine_test_32')
    >>> assert get_wine_registry_path(wine_prefix='wine_test_32').startswith('c:\\\\test;')
    >>> write_wine_registry_path(path=old_path, wine_prefix='wine_test_32')
    >>> assert get_wine_registry_path(wine_prefix='wine_test_32') == old_path

    """
    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    current_wine_registry_path = get_wine_registry_path(wine_prefix=wine_prefix, username=username)
    s_path_to_add = str(path_to_add).strip()
    l_current_wine_registry_path = current_wine_registry_path.split(';')
    l_current_wine_registry_path = lib_list.ls_strip_elements(l_current_wine_registry_path)
    # the path must not end with \\ , because if we set it this might escape the last " !!!
    # like : wine reg add "..." /t "REG_EXPAND_SZ" /v "PATH" /d "c:\test\" /f  leads to : /bin/sh: 1: Syntax error: Unterminated quoted string
    l_current_wine_registry_path = lib_list.ls_rstrip_elements(l_current_wine_registry_path, '\\')
    l_current_wine_registry_path = lib_list.del_double_elements(l_current_wine_registry_path)
    if not lib_list.is_list_element_fnmatching(ls_elements=l_current_wine_registry_path, s_fnmatch_searchpattern=s_path_to_add):
        l_current_wine_registry_path = [s_path_to_add] + l_current_wine_registry_path
    new_wine_registry_path = ';'.join(l_current_wine_registry_path)
    write_wine_registry_path(path=new_wine_registry_path, wine_prefix=wine_prefix, username=username)


def get_wine_registry_path(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                           username: str = configmagick_linux.get_current_username()) -> str:
    """
    >>> install_wine_machine.create_wine_test_prefixes()
    >>> result = get_wine_registry_path(wine_prefix='wine_test_32')
    >>> assert 'c:\\windows' in result.lower()
    >>> result = get_wine_registry_path(wine_prefix='wine_test_64')
    >>> assert 'c:\\windows' in result.lower()

    """
    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    current_wine_registry_path = get_wine_registry_data(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                                                        reg_subkey='PATH',
                                                        wine_prefix=wine_prefix,
                                                        username=username)
    return current_wine_registry_path


def write_wine_registry_path(path: str,
                             wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                             username: str = configmagick_linux.get_current_username()) -> None:
    """
    >>> install_wine_machine.create_wine_test_prefixes()
    >>> old_path = get_wine_registry_path(wine_prefix='wine_test_32')
    >>> write_wine_registry_path(path='c:\\\\test', wine_prefix='wine_test_32')
    >>> assert get_wine_registry_path(wine_prefix='wine_test_32') == 'c:\\\\test'
    >>> write_wine_registry_path(path=old_path, wine_prefix='wine_test_32')
    >>> restored_path = get_wine_registry_path(wine_prefix='wine_test_32')
    >>> assert restored_path == old_path

    """

    # the path must not end with \\ , because if we set it this might escape the last " !!!
    # like : wine reg add "..." /t "REG_EXPAND_SZ" /v "PATH" /d "c:\test\" /f  leads to : /bin/sh: 1: Syntax error: Unterminated quoted string
    path = path.strip().rstrip('\\')
    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    write_wine_registry_data(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                             reg_subkey='PATH',
                             reg_data=path,
                             wine_prefix=wine_prefix,
                             username=username)


def get_wine_registry_data(reg_key: str,
                           reg_subkey: str,
                           wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                           username: str = configmagick_linux.get_current_username()) -> str:
    """
    >>> install_wine_machine.create_wine_test_prefixes()
    >>> result = get_wine_registry_data(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                        reg_subkey='PATH', wine_prefix='wine_test_32')
    >>> assert 'c:\\windows' in result.lower()

    >>> result = get_wine_registry_data(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                        reg_subkey='PATH', wine_prefix='wine_test_64')
    >>> assert 'c:\\windows' in result.lower()

    >>> result = get_wine_registry_data(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                        reg_subkey='UNKNOWN', wine_prefix='wine_test_32')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    RuntimeError: can not read Wine Registry, WINEPREFIX=".../wine_test_32", key="...", subkey="UNKNOWN"
    """
    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    try:
        registry_data = get_l_wine_registry_data_struct(reg_key=reg_key, reg_subkey=reg_subkey, wine_prefix=wine_prefix, username=username)[1]
        return registry_data
    except subprocess.CalledProcessError:
        raise RuntimeError('can not read Wine Registry Data, WINEPREFIX="{wine_prefix}", key="{reg_key}", subkey="{reg_subkey}"'.format(
            wine_prefix=wine_prefix, reg_key=reg_key, reg_subkey=reg_subkey))


def get_wine_registry_data_type(reg_key: str,
                                reg_subkey: str,
                                wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                                username: str = configmagick_linux.get_current_username()) -> str:
    """
    >>> install_wine_machine.create_wine_test_prefixes()
    >>> result = get_wine_registry_data_type(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                             reg_subkey='PATH', wine_prefix='wine_test_32')
    >>> assert result == 'REG_EXPAND_SZ'

    >>> result = get_wine_registry_data_type(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                             reg_subkey='PATH', wine_prefix='wine_test_64')
    >>> assert result == 'REG_EXPAND_SZ'

    >>> result = get_wine_registry_data_type(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                             reg_subkey='UNKNOWN', wine_prefix='wine_test_32')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    RuntimeError: can not read Wine Registry Data Type, WINEPREFIX=".../wine_test_32", key="...", subkey="UNKNOWN"
    """
    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    try:
        registry_data_type = get_l_wine_registry_data_struct(reg_key=reg_key, reg_subkey=reg_subkey, wine_prefix=wine_prefix, username=username)[0]
        return registry_data_type
    except RuntimeError:
        raise RuntimeError('can not read Wine Registry Data Type, WINEPREFIX="{wine_prefix}", key="{reg_key}", subkey="{reg_subkey}"'.format(
            wine_prefix=wine_prefix, reg_key=reg_key, reg_subkey=reg_subkey))


def get_l_wine_registry_data_struct(reg_key: str,
                                    reg_subkey: str,
                                    wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                                    username: str = configmagick_linux.get_current_username()) -> Tuple[str, str]:
    """
    :returns [data_type, data]
    >>> install_wine_machine.create_wine_test_prefixes()
    >>> result = get_l_wine_registry_data_struct(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                                 reg_subkey='PATH', wine_prefix='wine_test_32')
    >>> assert result[0] == 'REG_EXPAND_SZ'
    >>> assert 'c:\\windows' in result[1].lower()

    >>> result = get_l_wine_registry_data_struct(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                                 reg_subkey='PATH', wine_prefix='wine_test_64')
    >>> assert result[0] == 'REG_EXPAND_SZ'
    >>> assert 'c:\\windows' in result[1].lower()

    >>> result = get_l_wine_registry_data_struct(reg_key='HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',\
                                                 reg_subkey='UNKNOWN', wine_prefix='wine_test_32')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    RuntimeError: can not read Wine Registry, WINEPREFIX=".../wine_test_32", key="...", subkey="UNKNOWN"
    """
    try:
        wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
        wine_arch = get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
        command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine reg query "{reg_key}" /v "{reg_subkey}"'.format(
            wine_prefix=wine_prefix, wine_arch=wine_arch, reg_key=reg_key, reg_subkey=reg_subkey)
        result = lib_shell.run_shell_command(command, quiet=True, shell=True, run_as_user=username)
        registry_string = result.stdout.split(reg_key)[1]           # because there may be blanks in the key
        registry_string = registry_string.split(reg_subkey)[1]      # and there might be blanks in the subkey
        l_registry_data = registry_string.split(maxsplit=1)         # here we split data_type and Data, there might be blanks in the data
        return l_registry_data[0], l_registry_data[1]
    except subprocess.CalledProcessError:
        raise RuntimeError('can not read Wine Registry, WINEPREFIX="{wine_prefix}", key="{reg_key}", subkey="{reg_subkey}"'.format(
            wine_prefix=wine_prefix, reg_key=reg_key, reg_subkey=reg_subkey))


def write_wine_registry_data(reg_key: str,
                             reg_subkey: str,
                             reg_data: str,
                             reg_data_type: str = 'auto',
                             wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                             username: str = configmagick_linux.get_current_username()) -> None:
    """ write wine registry data
    Parameter:
        reg_data_type:   'auto' to get the data type if the key already exists, otherwise put 'REG_SZ' or 'REG_EXPAND_SZ'


    """

    wine_prefix = get_and_check_wine_prefix(wine_prefix=wine_prefix, username=username)
    try:
        wine_arch = get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
        if reg_data_type == 'auto':
            reg_data_type = get_wine_registry_data_type(reg_key=reg_key, reg_subkey=reg_subkey, wine_prefix=wine_prefix, username=username)
        command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine reg add "{reg_key}" /t "{reg_data_type}" /v "{reg_subkey}" /d "{reg_data}" /f'\
                  .format(wine_prefix=wine_prefix, wine_arch=wine_arch, reg_key=reg_key, reg_data_type=reg_data_type, reg_subkey=reg_subkey, reg_data=reg_data)
        lib_shell.run_shell_command(command, quiet=True, shell=True, run_as_user=username)
    except subprocess.CalledProcessError:
        raise RuntimeError('can not write Wine Registry, WINEPREFIX="{wine_prefix}", key="{reg_key}", subkey="{reg_subkey}"'.format(
            wine_prefix=wine_prefix, reg_key=reg_key, reg_subkey=reg_subkey))
