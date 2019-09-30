# this __init__.py is only meant for local package development

try:
    from .configmagick_wine import *
    # this we need for pip install --install-option test
except ImportError:
    import configmagick_wine
