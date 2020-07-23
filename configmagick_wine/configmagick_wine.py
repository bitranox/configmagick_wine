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
    from . import install_gecko          # type: ignore # pragma: no cover
    from . import install_git            # type: ignore # pragma: no cover
    from . import install_wine                # type: ignore # pragma: no cover
    from . import install_wine_machine        # type: ignore # pragma: no cover
    from . import install_mono           # type: ignore # pragma: no cover
    from . import install_python         # type: ignore # pragma: no cover
    from . import install_python_nuget   # type: ignore # pragma: no cover
except ImportError:                           # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import lib_wine                           # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_gecko                 # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_git                   # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_wine                       # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_wine_machine               # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_mono                  # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_python                # type: ignore # pragma: no cover
    # noinspection PyUnresolvedReferences
    import install_python_nuget          # type: ignore # pragma: no cover


def main() -> None:
    # noinspection PyBroadException
    try:
        lib_log_utils.log_settings.use_colored_stream_handler = True
        # we must not call fire if the program is called via pytest
        is_called_via_pytest = [(sys_arg != '') for sys_arg in sys.argv if 'pytest' in sys_arg]
        if not is_called_via_pytest:
            fire.Fire({
                'install_wine': install_wine.install_wine,
                'install_winetricks': install_wine.install_winetricks,
                'update_winetricks': install_wine.update_winetricks,
                'install_wine_machine': install_wine_machine.install_wine_machine,
                'disable_gui_crash_dialogs': install_wine_machine.disable_gui_crash_dialogs,
                'set_windows_version': install_wine_machine.set_windows_version,
                'install_mono_latest': install_mono.install_mono_latest,
                'install_mono_recommended': install_mono.install_mono_recommended,
                'install_gecko': install_gecko.install_gecko,
                'install_git': install_git.install_git,
                'install_python': install_python.install_python,
                'install_python_nuget': install_python_nuget.install_python_nuget,
                'fix_permissions': lib_wine.fix_wine_permissions,
            })

    except FileNotFoundError:
        # see https://www.thegeekstuff.com/2010/10/linux-error-codes for error codes
        # No such file or directory
        lib_log_utils.log_traceback.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.ENOENT)                                                      # pragma: no cover
    except FileExistsError:
        # File exists
        lib_log_utils.log_traceback.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EEXIST)                                                      # pragma: no cover
    except TypeError:
        # Invalid Argument
        lib_log_utils.log_traceback.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EINVAL)                                                      # pragma: no cover
    except ValueError:
        # Invalid Argument
        lib_log_utils.log_traceback.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EINVAL)                                                      # pragma: no cover
    except RuntimeError:
        # Operation not permitted
        lib_log_utils.log_traceback.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EPERM)                                                       # pragma: no cover
    except Exception:
        # Operation not permitted
        lib_log_utils.log_traceback.log_exception_traceback(s_error='Unexpected Exception')       # pragma: no cover
        sys.exit(errno.EPERM)                                                       # pragma: no cover


if __name__ == '__main__':
    main()
