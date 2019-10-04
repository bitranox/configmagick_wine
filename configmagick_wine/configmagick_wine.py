# ####### STDLIB

import errno
# noinspection PyUnresolvedReferences
import getpass
# noinspection PyUnresolvedReferences
import logging
# noinspection PyUnresolvedReferences
import sys

# ####### EXT

# noinspection PyBroadException
try:
    import fire                             # type: ignore
except Exception:
    # maybe we dont need fire if not called via commandline, so accept if it is not there
    pass

# ####### OWN

# noinspection PyUnresolvedReferences
import lib_log_utils

# ####### PROJ

# imports for local pytest
try:
    from .wine_install import *         # type: ignore # pragma: no cover
# imports for doctest
except ImportError:                 # type: ignore # pragma: no cover
    from wine_install import *          # type: ignore # pragma: no cover


def main() -> None:
    try:
        lib_log_utils.BannerSettings.called_via_commandline = True
        # we must not call fire if the program is called via pytest
        is_called_via_pytest = [(sys_arg != '') for sys_arg in sys.argv if 'pytest' in sys_arg]
        if not is_called_via_pytest:
            fire.Fire({
                'install_wine': install_wine,
            })

    except FileNotFoundError:
        # see https://www.thegeekstuff.com/2010/10/linux-error-codes for error codes
        # No such file or directory
        sys.exit(errno.ENOENT)      # pragma: no cover
    except FileExistsError:
        # File exists
        sys.exit(errno.EEXIST)      # pragma: no cover
    except TypeError:
        # Invalid Argument
        sys.exit(errno.EINVAL)      # pragma: no cover
        # Invalid Argument
    except ValueError:
        sys.exit(errno.EINVAL)      # pragma: no cover


if __name__ == '__main__':
    main()
