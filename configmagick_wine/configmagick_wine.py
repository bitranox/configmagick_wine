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
    from . import lib_wine                    # type: ignore # pragma: no cover
    from . import wine_gecko_install          # type: ignore # pragma: no cover
    from . import wine_git_install            # type: ignore # pragma: no cover
    from . import wine_install                # type: ignore # pragma: no cover
    from . import wine_machine_install        # type: ignore # pragma: no cover
    from . import wine_mono_install           # type: ignore # pragma: no cover
    from . import wine_python_install         # type: ignore # pragma: no cover
    from . import wine_python_install_travis  # type: ignore # pragma: no cover
except ImportError:                           # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                           # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_gecko_install                 # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_git_install                   # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_install                       # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_machine_install               # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_mono_install                  # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_python_install                # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import wine_python_install_travis         # type: ignore # pragma: no cover


def main() -> None:
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
                'install_wine_git': wine_git_install.install_wine_git,
                'install_wine_python': wine_python_install.install_wine_python,
                'install_wine_python_webinstall': wine_python_install.install_wine_python_webinstall,
                'install_wine_python_travis': wine_python_install_travis.install_wine_python_travis,
                'fix_wine_permissions': lib_wine.fix_wine_permissions,
            })

    except FileNotFoundError:
        # see https://www.thegeekstuff.com/2010/10/linux-error-codes for error codes
        # No such file or directory
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.ENOENT)                                                      # pragma: no cover
    except FileExistsError:
        # File exists
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EEXIST)                                                      # pragma: no cover
    except TypeError:
        # Invalid Argument
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EINVAL)                                                      # pragma: no cover
    except ValueError:
        # Invalid Argument
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EINVAL)                                                      # pragma: no cover
    except RuntimeError:
        # Operation not permitted
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EPERM)                                                       # pragma: no cover
    except Exception:
        # Operation not permitted
        lib_log_utils.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EPERM)                                                       # pragma: no cover


if __name__ == '__main__':
    main()
