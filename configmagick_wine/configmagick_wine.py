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
    # noinspection PyPackageRequirements
    import fire                             # type: ignore
except Exception:
    # maybe we dont need fire if not called via commandline, so accept if it is not there
    pass

# ####### OWN

# noinspection PyUnresolvedReferences
import lib_log_utils

# ####### PROJ

try:
    # imports for local pytest
    from . import wine_install              # type: ignore # pragma: no cover
    from . import wine_machine_install      # type: ignore # pragma: no cover
    from . import wine_mono_install         # type: ignore # pragma: no cover
    from . import wine_gecko_install        # type: ignore # pragma: no cover
    from . import lib_wine                  # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import wine_install                     # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_machine_install             # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_mono_install                # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_gecko_install               # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import lib_wine                         # type: ignore # pragma: no cover


def main() -> None:
    exit_code = 0
    # noinspection PyBroadException
    try:
        lib_log_utils.BannerSettings.called_via_commandline = True
        # we must not call fire if the program is called via pytest
        is_called_via_pytest = [(sys_arg != '') for sys_arg in sys.argv if 'pytest' in sys_arg]
        if not is_called_via_pytest:
            fire.Fire({
                'install_wine': wine_install.install_wine,
                'install_winetricks': wine_install.install_winetricks,
                'update_winetricks': wine_install.update_winetricks,
                'install_wine_machine': wine_machine_install.install_wine_machine,
                'disable_gui_crash_dialogs': wine_machine_install.disable_gui_crash_dialogs,
                'set_windows_version': wine_machine_install.set_windows_version,
                'install_wine_mono_latest': wine_mono_install.install_wine_mono_latest,
                'install_wine_mono_recommended': wine_mono_install.install_wine_mono_recommended,
                'install_wine_gecko': wine_gecko_install.install_wine_gecko,
                'fix_wine_permissions': lib_wine.fix_wine_permissions,
            })

    except FileNotFoundError:
        # see https://www.thegeekstuff.com/2010/10/linux-error-codes for error codes
        # No such file or directory
        exit_code = errno.ENOENT      # pragma: no cover
    except FileExistsError:
        # File exists
        exit_code = errno.EEXIST       # pragma: no cover
    except TypeError:
        # Invalid Argument
        exit_code = errno.EINVAL       # pragma: no cover
    except ValueError:
        # Invalid Argument
        exit_code = errno.EINVAL       # pragma: no cover
    except RuntimeError:
        # Operation not permitted
        exit_code = errno.EPERM       # pragma: no cover
    except Exception:
        # Operation not permitted
        exit_code = errno.EPERM       # pragma: no cover
    finally:
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
