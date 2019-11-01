# STDLIB
import os

# OWN
import configmagick_linux
import lib_log_utils

# ####### PROJ
try:
    # imports for local pytest
    from . import wine_python_install   # type: ignore # pragma: no cover
except ImportError:                     # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import wine_python_install          # type: ignore # pragma: no cover


def travis_workaround() -> None:
    """
    >>> if 'WINEPREFIX' in os.environ:
    ...     wine_prefix = os.environ['WINEPREFIX']
    ... else:
    ...     wine_prefix = ''

    >>> lib_log_utils.banner_notice('install_wine_python_travis, WINEPREFIX="{wine_prefix}", on_travis="{is_on_travis}"'\
                    .format(wine_prefix=wine_prefix, is_on_travis=configmagick_linux.is_on_travis() ))

    >>> if ('WINEPREFIX' in os.environ) and configmagick_linux.is_on_travis():
    ...     wine_prefix = os.environ['WINEPREFIX']
    ...     lib_log_utils.banner_notice('install_wine_python_travis, WINEPREFIX="{wine_prefix}"'.format(wine_prefix=wine_prefix))
    ...     wine_python_install.install_wine_python(wine_prefix=wine_prefix, quiet=False)
    ...     lib_log_utils.banner_notice('after install_wine_python_travis')


    """
    pass


def install_wine_python_travis() -> None:
    import doctest
    doctest.testmod()
