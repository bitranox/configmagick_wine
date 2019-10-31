# STDLIB
import os

# OWN
import configmagick_linux

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
    >>> if 'WINEPREFIX' in os.environ and configmagick_linux.is_on_travis():
    ...     wine_prefix = os.environ['WINEPREFIX']
    ...     wine_python_install.install_wine_python(wine_prefix=wine_prefix, quiet=True)

    """
    pass
