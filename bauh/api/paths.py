from getpass import getuser
from pathlib import Path

from bauh import __app_name__
from bauh.api import user

CACHE_PATH = f'/var/cache/{__app_name__}' if user.is_root() else f'{Path.home()}/.cache/{__app_name__}'
CONFIG_DIR = f'/etc/{__app_name__}' if user.is_root() else f'{Path.home()}/.config/{__app_name__}'
USER_THEMES_PATH = '{}/.local/share/bauh/themes'.format(str(Path.home()))
DESKTOP_ENTRIES_DIR = '{}/.local/share/applications'.format(str(Path.home()))
TEMP_DIR = f'/tmp/{__app_name__}@{getuser()}'
LOGS_DIR = f'{TEMP_DIR}/logs'
AUTOSTART_DIR = f'/etc/xdg/autostart' if user.is_root() else f'{Path.home()}/.config/autostart'
