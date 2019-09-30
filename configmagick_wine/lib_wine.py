# ### STDLIB
import logging

# ### OWN
import configmagick_linux
import lib_log_utils


def install_wine(wine_release: str = '') -> int:
    return_code = 0
    lib_log_utils.banner_success('Installing WINE and WINETRICKS: \n'
                                 'linux_release_name = {linux_release_name} \n'
                                 'wine_release = {wine_release} \n'.format(linux_release_name='x',
                                                                           wine_release=wine_release))

    return return_code
