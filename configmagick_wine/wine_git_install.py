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


def install_wine_git(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                     username: str = configmagick_linux.get_current_username(),
                     quiet: bool = False) -> None:

    """ install git on wine

    >>> wine_machine_install.create_wine_test_prefixes()
    >>> install_wine_git(wine_prefix='wine_test_32', quiet=True)
    >>> install_wine_git(wine_prefix='wine_test_64', quiet=True)

    """
    configmagick_linux.full_update_and_upgrade(quiet=quiet)
    configmagick_linux.install_linux_package('p7zip-full', quiet=quiet)
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)
    wine_cache_directory = lib_wine.get_path_wine_cache_for_user(username=username)
    path_git_filename = get_path_git_filename(wine_arch=wine_arch)
    lib_log_utils.banner_verbose('Installing Git Portable :\n'
                                 'WINEPREFIX="{wine_prefix}"\n'
                                 'WINEARCH="{wine_arch}"\n'
                                 'git_filename="{path_git_filename}"\n'
                                 'wine_cache_directory="{wine_cache_directory}"'
                                 .format(wine_prefix=wine_prefix,
                                         wine_arch=wine_arch,
                                         path_git_filename=path_git_filename,
                                         wine_cache_directory=wine_cache_directory),
                                 quiet=quiet)

    download_latest_git_files_from_github_to_winecache(wine_prefix=wine_prefix, username=username, quiet=quiet)
    lib_log_utils.log_verbose('Install "{path_git_filename}" on WINEPREFIX="{wine_prefix}"'
                              .format(path_git_filename=path_git_filename, wine_prefix=wine_prefix), quiet=quiet)

    path_git_install_dir = wine_prefix / 'drive_c/Program Files/PortableGit'

    lib_shell.run_shell_command('rm -Rf "{path_git_install_dir}"'.format(path_git_install_dir=path_git_install_dir), quiet=True, use_sudo=True, shell=True)
    # remove old installation if exists
    configmagick_linux.force_remove_directory_recursive(path_git_install_dir)
    command = '7z e {wine_cache_directory}/{path_git_filename} -o"{path_git_install_dir}" -y -bd'.format(
        wine_cache_directory=wine_cache_directory,
        path_git_filename=path_git_filename,
        path_git_install_dir=path_git_install_dir)
    lib_shell.run_shell_command(command, shell=True, run_as_user=username, pass_stdout_stderr_to_sys=True, quiet=quiet)
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)   # it is cheap, just in case
    lib_wine.prepend_path_to_wine_registry_path(path_to_add='C:\\Program Files\\PortableGit', wine_prefix=wine_prefix, username=username)
    # we need to use wineconsole here
    command = 'WINEPREFIX="{wine_prefix}" WINEARCH="{wine_arch}" wineconsole git --version'.format(wine_prefix=wine_prefix, wine_arch=wine_arch)
    try:
        lib_shell.run_shell_command(command, run_as_user=username, quiet=True, shell=True)
        lib_log_utils.banner_success('Git installed')
    except subprocess.CalledProcessError:
        raise RuntimeError('can not install git portable on WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))


def download_latest_git_files_from_github_to_winecache(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                                                       username: str = configmagick_linux.get_current_username(),
                                                       force_download: bool = False,
                                                       quiet: bool = False) -> None:

    """
    >>> wine_machine_install.create_wine_test_prefixes()
    >>> download_latest_git_files_from_github_to_winecache(wine_prefix = 'wine_test_32', force_download=True, quiet=False)
    >>> download_latest_git_files_from_github_to_winecache(wine_prefix = 'wine_test_64', force_download=False, quiet=False)
    """
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)
    wine_arch = lib_wine.get_wine_arch_from_wine_prefix(wine_prefix=wine_prefix, username=username)

    lib_log_utils.log_verbose('Download latest Portable Git from Github to Wine Cache', quiet=quiet)
    git_download_link = get_git_portable_download_link_from_github(wine_arch=wine_arch)
    git_exe_filename = pathlib.Path(git_download_link.rsplit('/', 1)[1])

    if lib_wine.is_file_in_wine_cache(filename=git_exe_filename, username=username) or force_download:
        if force_download:
            lib_wine.remove_file_from_winecache(filename=git_exe_filename, username=username)
            lib_wine.download_file_to_winecache(download_link=git_download_link, filename=git_exe_filename, username=username)
    else:
        lib_wine.download_file_to_winecache(download_link=git_download_link, filename=git_exe_filename, username=username)


def get_git_portable_download_link_from_github(wine_arch: str) -> str:
    """
    Parameter:
        wine_arch = win32 or win64

    >>> get_git_portable_download_link_from_github(wine_arch='win32')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    'https://github.com/git-for-windows/git/releases/download/v...windows.1/PortableGit-...-32-bit.7z.exe'

    >>> get_git_portable_download_link_from_github(wine_arch='win64')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    'https://github.com/git-for-windows/git/releases/download/v...windows.1/PortableGit-...-64-bit.7z.exe'

    >>> get_git_portable_download_link_from_github(wine_arch='invalid')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    subprocess.CalledProcessError: ...

    """
    filename = configmagick_linux.get_path_home_dir_current_user() / 'git-latest-release.html'
    try:
        download_link = 'https://github.com/git-for-windows/git/releases/latest'
        configmagick_linux.download_file(download_link=download_link, filename=filename)
        link = lib_shell.run_shell_command('fgrep "PortableGit-" "{filename}" | fgrep "{bit}-bit.7z.exe" | fgrep "href="'
                                           .format(filename=filename, bit=wine_arch[3:]),
                                           shell=True, quiet=True, use_sudo=True).stdout
        link = link.split('href="', 1)[1]
        link = 'https://github.com' + link.split('"', 1)[0]
    finally:
        lib_shell.run_shell_command('rm -f "{filename}"'.format(filename=filename), shell=True, quiet=True, use_sudo=True)
    return str(link)


def get_path_git_filename(wine_arch: str) -> pathlib.Path:
    """
    >>> get_path_git_filename(wine_arch = 'win32')   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    PosixPath('PortableGit-...-32-bit.7z.exe')
    >>> get_path_git_filename(wine_arch = 'win64')   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    PosixPath('PortableGit-...-64-bit.7z.exe')

    """

    git_portable_download_link = get_git_portable_download_link_from_github(wine_arch=wine_arch)
    path_git_filename = pathlib.Path(git_portable_download_link.rsplit('/', 1)[1])
    return path_git_filename
