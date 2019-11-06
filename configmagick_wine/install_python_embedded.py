# ### STDLIB
import pathlib
import subprocess
from typing import Union

# ### OWN
import configmagick_linux
import lib_log_utils
import lib_shell

# ####### PROJ
try:
    # imports for local pytest
    from . import lib_wine                      # type: ignore # pragma: no cover
    from . import install_python_setuptools     # type: ignore # pragma: no cover
    from . import install_wine                  # type: ignore # pragma: no cover
    from . import install_wine_machine          # type: ignore # pragma: no cover
except ImportError:                             # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                             # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_python_setuptools            # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_wine                         # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_wine_machine                 # type: ignore # pragma: no cover


def install_python_embedded(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                            username: str = configmagick_linux.get_current_username(),
                            python_version: str = 'latest',
                            quiet: bool = False) -> None:

    """ install python on wine, using the normal installer - unfortunately this does not work on travis

    Parameter:
        python_version : 'latest' or valid Version number, like '3.8.0'

    >>> # install_wine_machine.create_wine_test_prefixes()
    >>> # install_python_embedded(wine_prefix='wine_test_32', quiet=True)
    >>> # install_python_embedded(wine_prefix='wine_test_64', quiet=True)

    >>> install_python_setuptools.install_python_setuptools(wine_prefix='wine_test_32', quiet=True)
    >>> install_python_setuptools.install_python_setuptools(wine_prefix='wine_test_64', quiet=True)

    >>> # test python 32 Bit installed
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix='wine_test_32')
    >>> wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix)
    >>> command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine '
    >>> result = lib_shell.run_shell_command('WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine python --version'
    ...                                      .format(wine_prefix=wine_prefix, wine_arch=wine_arch), shell=True, quiet=True)
    >>> assert result.stdout.startswith('Python')
    >>> assert '.' in result.stdout

    >>> # test python 64 Bit installed
    >>> wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix='wine_test_64')
    >>> wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix)
    >>> command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine '
    >>> result = lib_shell.run_shell_command('WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine python --version'
    ...                                      .format(wine_prefix=wine_prefix, wine_arch=wine_arch), shell=True, quiet=True)
    >>> assert result.stdout.startswith('Python')
    >>> assert '.' in result.stdout

    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    if python_version == 'latest':
        python_version = get_latest_python_version()
    path_python_zip_filename = get_path_python_zip_filename(version=python_version, arch=wine_arch)
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    lib_log_utils.banner_verbose('Installing Python :\n'
                                 'WINEPREFIX="{wine_prefix}"\n'
                                 'WINEARCH="{wine_arch}"\n'
                                 'python_zip_file="{path_python_zip_filename}"\n'
                                 'wine_cache_directory="{wine_cache_directory}"'
                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         wine_cache_directory=wine_cache_directory,
                                         path_python_zip_filename=path_python_zip_filename),
                                 quiet=quiet)

    download_python_zip_file(python_version=python_version, wine_prefix=wine_prefix, username=username)

    lib_log_utils.log_verbose('Install "{path_python_zip_filename}" on WINEPREFIX="{wine_prefix}"'
                              .format(path_python_zip_filename=path_python_zip_filename, wine_prefix=wine_prefix), quiet=quiet)

    python_path_linux = get_python_path_linux(wine_prefix=wine_prefix, python_version=python_version, wine_arch=wine_arch)

    command = 'unzip -o {wine_cache_directory}/{path_python_zip_filename} -d "{python_path_linux}"'.format(
        wine_cache_directory=wine_cache_directory,
        path_python_zip_filename=path_python_zip_filename,
        python_path_linux=python_path_linux)

    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)
    python_path_windows = get_python_path_windows(python_version=python_version, wine_arch=wine_arch)
    lib_wine.prepend_path_to_wine_registry_path(python_path_windows, wine_prefix=wine_prefix, username=username)

    try:
        command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine python --version'.format(wine_prefix=wine_prefix, wine_arch=wine_arch)
        result = lib_shell.run_shell_command(command, run_as_user=username, quiet=True, shell=True)
        assert result.stdout.startswith('Python')
        lib_log_utils.banner_success('{python_version} installed OK'.format(python_version=result.stdout), quiet=quiet)
    except (subprocess.CalledProcessError, AssertionError):
        raise RuntimeError('can not install Python on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))


def get_python_path_linux(wine_prefix: Union[str, pathlib.Path], python_version: str, wine_arch: str) -> str:
    """
    >>> assert get_python_path_linux(wine_prefix='/root/.wine', python_version='3.8.0', wine_arch='win32') == '/root/.wine/drive_c/Program Files/Python38-32'
    >>> assert get_python_path_linux(wine_prefix='/root/.wine', python_version='3.8.0', wine_arch='win64') == '/root/.wine/drive_c/Program Files/Python38-64'
    """
    version = python_version.split('.')[0] + python_version.split('.')[1]
    architecture = wine_arch[3:]
    python_path_linux = '{wine_prefix}/drive_c/Program Files/Python{version}-{architecture}'.format(
        wine_prefix=wine_prefix, version=version, architecture=architecture)
    return python_path_linux


def get_python_path_windows(python_version: str, wine_arch: str) -> str:
    """
    >>> assert get_python_path_windows(python_version='3.8.0', wine_arch='win32') == 'C:\\\\Program Files\\\\Python38-32'
    >>> assert get_python_path_windows(python_version='3.8.0', wine_arch='win64') == 'C:\\\\Program Files\\\\Python38-64'
    """
    version = python_version.split('.')[0] + python_version.split('.')[1]
    architecture = wine_arch[3:]
    python_path_windows = 'C:\\Program Files\\Python{version}-{architecture}'.format(version=version, architecture=architecture)
    return python_path_windows


def get_latest_python_version() -> str:
    """ get latest Python3 Version as String, or '3.8.0' if can not determined

    Returns:
         "3.8.0" or whatever is the latest Version Number

    >>> version = get_latest_python_version()
    >>> assert '.' in version
    >>> assert get_latest_python_version().startswith('3')
    """
    # noinspection PyBroadException
    filename = configmagick_linux.get_path_home_dir_current_user() / 'python-latest-release.html'
    try:
        download_link = 'https://www.python.org/downloads/windows/'
        configmagick_linux.download_file(download_link=download_link, filename=filename)

        s_version = lib_shell.run_shell_command('fgrep "Latest Python 3 Release" "{filename}" | fgrep "href="'
                                                .format(filename=filename), shell=True, quiet=True, use_sudo=True).stdout
        # <li><a href="/downloads/release/python-380/">Latest Python 3 Release - Python 3.8.0</a></li>
        s_version = s_version.rsplit('Latest Python 3 Release', 1)[1]    # - Python 3.8.0</a></li>
        s_version = s_version.split('Python', 1)[1].strip()  # 3.8.0</a></li>
        s_version = s_version.split('</a>', 1)[0].strip()  # 3.8.0
    except Exception:
        lib_log_utils.log_warning('can not determine latest Python Version, assuming Version 3.8.0')
        s_version = '3.8.0'
    finally:
        lib_shell.run_shell_command('rm -f "{filename}"'.format(filename=filename), shell=True, quiet=True, use_sudo=True)
    return str(s_version)


def get_python_zip_download_link(version: str, arch: str = 'win32') -> str:
    """ get the download link for the python version by convention how the link should look like to the python installer exe
    Parameter:
        version = '3.8.0'
        arch = 'win32' or 'win64'

    >>> import unittest
    >>> assert get_python_zip_download_link(version='3.8.0', arch='win32') == 'https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-win32.zip'
    >>> assert get_python_zip_download_link(version='3.8.0', arch='win64') == 'https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-amd64.zip'
    >>> unittest.TestCase().assertRaises(RuntimeError, get_python_zip_download_link, version='3.8.0', arch='invalid')

    """
    arch = lib_wine.get_and_check_wine_arch_valid(arch)
    if arch == 'win32':
        python_download_link = 'https://www.python.org/ftp/python/{version}/python-{version}-embed-win32.zip'.format(version=version)
    else:
        python_download_link = 'https://www.python.org/ftp/python/{version}/python-{version}-embed-amd64.zip'.format(version=version)
    return str(python_download_link)


def get_python_zip_backup_download_link(version: str, arch: str = 'win32') -> str:
    """ get the download link for the python version from the webpage to the python installer exe
    Parameter:
        version = '3.8.0'
        arch = 'win32' or 'win64'

    >>> import unittest
    >>> assert get_python_zip_backup_download_link(version='3.8.0', arch='win32') == 'https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-win32.zip'
    >>> assert get_python_zip_backup_download_link(version='3.8.0', arch='win64') == 'https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-amd64.zip'
    >>> unittest.TestCase().assertRaises(RuntimeError, get_python_zip_backup_download_link, version='3.8.0', arch='invalid')    # invalid arch
    >>> unittest.TestCase().assertRaises(RuntimeError, get_python_zip_backup_download_link, version='3.1.9', arch='win32')      # invalid version

    """
    # noinspection PyBroadException
    arch = lib_wine.get_and_check_wine_arch_valid(arch)
    filename = configmagick_linux.get_path_home_dir_current_user() / 'python-latest-release.html'
    path_python_filename = get_path_python_zip_filename(version=version, arch=arch)
    try:
        download_link = 'https://www.python.org/downloads/windows/'
        configmagick_linux.download_file(download_link=download_link, filename=filename)

        python_backup_download_link = lib_shell.run_shell_command('fgrep "{path_python_filename}" "{filename}" | fgrep "href="'
                                                                  .format(filename=filename, path_python_filename=path_python_filename),
                                                                  shell=True, quiet=True, use_sudo=True).stdout
        # <li>Download <a href="https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe">Windows x86-64 executable installer</a></li>
        python_backup_download_link = python_backup_download_link.split('<a href="')[1]
        # https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe">Windows x86-64 executable installer</a></li>
        python_backup_download_link = python_backup_download_link.split('"')[0].strip()
        # https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe
    except Exception:
        raise RuntimeError('can not get Download Link for Python {path_python_filename}'.format(path_python_filename=path_python_filename))
    finally:
        lib_shell.run_shell_command('rm -f "{filename}"'.format(filename=filename), shell=True, quiet=True, use_sudo=True)
    return str(python_backup_download_link)


def get_path_python_zip_filename(version: str, arch: str = 'win32') -> pathlib.Path:
    """ get the filename of the .exe Setup File

    >>> assert str(get_path_python_zip_filename(version='3.8.0', arch='win32')) == 'python-3.8.0-embed-win32.zip'
    >>> assert str(get_path_python_zip_filename(version='3.8.0', arch='win64')) == 'python-3.8.0-embed-amd64.zip'

    """
    arch = lib_wine.get_and_check_wine_arch_valid(arch)

    if arch == 'win32':
        path_python_filename = pathlib.Path('python-{version}-embed-win32.zip'.format(version=version))
    else:
        path_python_filename = pathlib.Path('python-{version}-embed-amd64.zip'.format(version=version))
    return path_python_filename


def download_python_zip_file(python_version: str, wine_prefix: Union[str, pathlib.Path],
                             username: str = configmagick_linux.get_current_username(), force_download: bool = False) -> None:
    """ Downloads the Python Embedded Zip File to the WineCache directory

    >>> install_wine_machine.create_wine_test_prefixes()
    >>> wine_prefix = configmagick_linux.get_path_home_dir_current_user() / 'wine_test_32'
    >>> wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix)
    >>> username = configmagick_linux.get_current_username()
    >>> python_version = get_latest_python_version()
    >>> path_python_filename = get_path_python_zip_filename(version=python_version, arch=wine_arch)
    >>> path_downloaded_file = configmagick_linux.get_path_home_dir_current_user() / '.cache/wine' / path_python_filename
    >>> if path_downloaded_file.is_file():
    ...    path_downloaded_file.unlink()
    >>> download_python_zip_file(python_version=python_version, wine_prefix=wine_prefix, username=username, force_download=True)
    >>> assert path_downloaded_file.is_file()
    >>> download_python_zip_file(python_version=python_version, wine_prefix=wine_prefix, username=username, force_download=False)
    >>> assert path_downloaded_file.is_file()

    >>> wine_prefix = configmagick_linux.get_path_home_dir_current_user() / 'wine_test_64'
    >>> wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix)
    >>> python_version = get_latest_python_version()
    >>> path_python_filename = get_path_python_zip_filename(version=python_version, arch=wine_arch)
    >>> path_downloaded_file = configmagick_linux.get_path_home_dir_current_user() / '.cache/wine' / path_python_filename
    >>> if path_downloaded_file.is_file():
    ...    path_downloaded_file.unlink()
    >>> download_python_zip_file(python_version=python_version, wine_prefix=wine_prefix, username=username, force_download=True)
    >>> assert path_downloaded_file.is_file()
    >>> download_python_zip_file(python_version=python_version, wine_prefix=wine_prefix, username=username, force_download=False)
    >>> assert path_downloaded_file.is_file()

    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    python_download_link = get_python_zip_download_link(version=python_version, arch=wine_arch)
    python_backup_download_link = get_python_zip_backup_download_link(version=python_version, arch=wine_arch)
    path_python_filename = get_path_python_zip_filename(version=python_version, arch=wine_arch)

    if lib_wine.is_file_in_wine_cache(filename=path_python_filename, username=username) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=path_python_filename, username=username)
        else:
            return

    try:
        lib_wine.download_file_to_winecache(download_link=python_download_link, filename=path_python_filename, username=username)
    except subprocess.CalledProcessError:
        lib_wine.download_file_to_winecache(download_link=python_backup_download_link, filename=path_python_filename, username=username)


def uncomment_import_site(python_path_linux: str) -> None:
    # python_path_linux/python38._pth
    # uncomment import site
    pass
