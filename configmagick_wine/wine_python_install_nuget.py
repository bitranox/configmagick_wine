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
    from . import lib_wine              # type: ignore # pragma: no cover
    from . import wine_install          # type: ignore # pragma: no cover
    from . import wine_machine_install  # type: ignore # pragma: no cover
except ImportError:                     # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                     # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_install                 # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_machine_install                 # type: ignore # pragma: no cover


class NullWriter(object):               # type: ignore # pragma: no cover
    def write(self, s):                 # type: ignore # pragma: no cover
        pass                            # type: ignore # pragma: no cover

    def flush(self):                    # type: ignore # pragma: no cover
        pass                            # type: ignore # pragma: no cover


def install_wine_python_nuget(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                              username: str = configmagick_linux.get_current_username(),
                              quiet: bool = True) -> None:

    """ install python on wine, using the normal installer - unfortunately this does not work on travis

    Parameter:
        python_version : 'latest' or valid Version number, like '3.8.0'

    >>> wine_machine_install.create_wine_test_prefixes()
    >>> install_wine_python_nuget(wine_prefix='wine_test_32', quiet=False)
    >>> install_wine_python_nuget(wine_prefix='wine_test_64', quiet=False)

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
    if wine_arch == 'win32':
        python_version = 'pythonx86'
    else:
        python_version = 'python'

    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    path_nuget_filename = pathlib.Path('nuget.exe')
    lib_log_utils.banner_verbose('Installing Python :\n'
                                 'WINEPREFIX="{wine_prefix}"\n'
                                 'WINEARCH="{wine_arch}"\n'
                                 'wine_cache_directory="{wine_cache_directory}"'
                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         wine_cache_directory=wine_cache_directory),
                                 quiet=quiet)

    download_nuget(username=username)

    lib_log_utils.log_verbose('Install Python on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix), quiet=quiet)

    command = 'DISPLAY="{display}" WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" '\
              'wine "{wine_cache_directory}/{path_nuget_filename}" '\
              'install {python_version} -ExcludeVersion -OutputDirectory "C:\\Program Files"'\
        .format(display=configmagick_linux.get_env_display(),
                wine_prefix=wine_prefix,
                wine_arch=wine_arch,
                wine_cache_directory=wine_cache_directory,
                path_nuget_filename=path_nuget_filename,
                python_version=python_version)

    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)
    lib_wine.prepend_path_to_wine_registry_path('C:\\Program Files\\{python_version}\\tools'.format(python_version=python_version),
                                                wine_prefix=wine_prefix, username=username)

    command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine python --version'.format(wine_prefix=wine_prefix, wine_arch=wine_arch)
    try:
        result = lib_shell.run_shell_command(command, run_as_user=username, quiet=True, shell=True)
        assert result.stdout.startswith('Python')
    except (subprocess.CalledProcessError, AssertionError):
        raise RuntimeError('can not install Python on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))


def download_nuget(username: str = configmagick_linux.get_current_username(), force_download: bool = False) -> None:
    """ Downloads nuget.exe to the WineCache directory

    >>> username = configmagick_linux.get_current_username()
    >>> path_nuget_filename = pathlib.Path('nuget.exe')
    >>> path_downloaded_file = configmagick_linux.get_path_home_dir_current_user() / '.cache/wine' / path_nuget_filename
    >>> if path_downloaded_file.is_file():
    ...    path_downloaded_file.unlink()
    >>> download_nuget(username=username, force_download=True)
    >>> assert path_downloaded_file.is_file()
    >>> download_nuget(username=username, force_download=False)
    >>> assert path_downloaded_file.is_file()

    """
    nuget_download_link = 'https://aka.ms/nugetclidl'
    path_nuget_filename = pathlib.Path('nuget.exe')

    if lib_wine.is_file_in_wine_cache(filename=path_nuget_filename, username=username) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=path_nuget_filename, username=username)
        else:
            return

    lib_wine.download_file_to_winecache(download_link=nuget_download_link, filename=path_nuget_filename, username=username)
