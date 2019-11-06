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
    from . import install_wine          # type: ignore # pragma: no cover
    from . import install_wine_machine  # type: ignore # pragma: no cover
except ImportError:                     # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                     # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_wine                 # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_wine_machine                 # type: ignore # pragma: no cover


def install_python_setuptools(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                              username: str = configmagick_linux.get_current_username(),
                              quiet: bool = False) -> None:


    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    download_get_pip(username=username)
    command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wine python "{wine_cache_directory}/get-pip.py"'.format(
        wine_prefix=wine_prefix, wine_arch=wine_arch, wine_cache_directory=wine_cache_directory)
    lib_shell.run_shell_command(command, run_as_user=username, quiet=True, shell=True)


def download_setup_tools(username: str = configmagick_linux.get_current_username(),
                         quiet: bool = False) -> None:
    """
    >>> download_setup_tools(quiet=True)
    >>> wine_cache_directory = lib_wine.get_path_wine_cache_for_user()
    >>> assert (wine_cache_directory / 'setuptools/easy_install.py').exists()

    """
    configmagick_linux.install_linux_package('git')
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    command = 'git clone https://github.com/pypa/setuptools.git {wine_cache_directory}/setuptools'.format(wine_cache_directory=wine_cache_directory)
    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)


def download_get_pip(username: str) -> None:
    """
    >>> username = configmagick_linux.get_current_username()
    >>> download_get_pip(username=username)
    >>> wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    >>> assert (wine_cache_directory / 'get-pip.py').exists()

    """
    download_link = 'https://bootstrap.pypa.io/get-pip.py'
    filename = pathlib.Path('get-pip.py')
    lib_wine.download_file_to_winecache(download_link=download_link, filename=filename, username=username)
