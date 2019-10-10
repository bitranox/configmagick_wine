# ### STDLIB
import pathlib
import time
from typing import Union

# ### OWN
import configmagick_linux
import lib_log_utils


# ####### PROJ

try:
    # imports for local pytest
    from . import lib_wine             # type: ignore # pragma: no cover
except ImportError:                    # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                    # type: ignore # pragma: no cover


def install_wine_gecko(wine_prefix: Union[str, pathlib.Path] = configmagick_linux.get_path_home_dir_current_user() / '.wine',
                       username: str = configmagick_linux.get_current_username()) -> None:
    wine_prefix = lib_wine.get_and_check_wine_prefix(wine_prefix, username)    # prepend /home/user if needed
    # TODO
    lib_wine.fix_wine_permissions(wine_prefix=wine_prefix, username=username)  # it is cheap, just in case
