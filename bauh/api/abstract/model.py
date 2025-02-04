from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Iterable

from bauh.api.paths import CACHE_DIR


class CustomSoftwareAction:

    def __init__(self, i18n_label_key: str, i18n_status_key: str, icon_path: str, manager_method: str,
                 requires_root: bool, manager: "SoftwareManager" = None,
                 backup: bool = False, refresh: bool = True,
                 i18n_confirm_key: str = None,
                 requires_internet: bool = False,
                 requires_confirmation: bool = True,
                 i18n_description_key: Optional[str] = None):
        """
        :param i18n_label_key: the i18n key that will be used to display the action name
        :param i18n_status_key: the i18n key that will be used to display the action name being executed
        :param icon_path: the action icon path. Use None for no icon
        :param manager_method: the SoftwareManager method name that should be called. The method must has the following parameters: (pkg: SoftwarePackage, root_password: Optional[str], watcher: ProcessWatcher)
        :param manager: the instance that will execute the action ( optional )
        :param backup: if a system backup should be performed before executing the action
        :param requires_root:
        :param refresh: if all displayed apps on the view should be refreshed if the action succeeds
        :param i18n_confirm_key: action confirmation message
        :param requires_internet: if the action requires internet connection to be executed
        :param requires_confirmation: if a confirmation popup should be displayed to the user before calling the action
        :param i18n_description_key: the i18n key for the action description
        """
        self.i18n_label_key = i18n_label_key
        self.i18n_status_key = i18n_status_key
        self.icon_path = icon_path
        self.manager_method = manager_method
        self.requires_root = requires_root
        self.manager = manager
        self.backup = backup
        self.refresh = refresh
        self.i18n_confirm_key = i18n_confirm_key
        self.requires_internet = requires_internet
        self.requires_confirmation = requires_confirmation
        self.i18n_description_key = i18n_description_key

    def __hash__(self) -> int:
        return sum(hash(val) for val in self.__dict__.values())

    def __eq__(self, other) -> bool:
        if isinstance(other, CustomSoftwareAction):
            return self.__dict__ == other.__dict__

        return False

    def __repr__(self):
        return f"{self.__class__.__name__} (label={self.i18n_label_key}, method={self.manager_method})"


class PackageStatus(Enum):
    READY = 1  # when all package data is already filled
    LOADING_DATA = 2  # when some package data is already being retrieved asynchronously


class SoftwarePackage(ABC):

    def __init__(self, id: str = None, version: str = None, name: str = None, description: str = None, latest_version: str = None,
                 icon_url: str = None, status: PackageStatus = PackageStatus.READY, installed: bool = False, update: bool = False,
                 size: int = None, categories: List[str] = None, license: str = None):
        """
        :param id:
        :param version:
        :param name:
        :param description:
        :param latest_version:
        :param icon_url: the path to the package icon. It can be an URL or PATH
        :param status:
        :param installed:
        :param update: if there is an update for package
        :param size: package size in BYTES
        :param categories: package categories. i.e: video editor, web browser, etc
        """
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.version = version
        self.latest_version = latest_version
        self.icon_url = icon_url
        self.installed = installed
        self.update = update
        self.size = size
        self.categories = categories
        self.license = license
        self.gem_name = self.__module__.split('.')[2]

    @abstractmethod
    def has_history(self):
        """
        :return: if the application has a commit history that can be shown to the user
        """
        pass

    @abstractmethod
    def has_info(self):
        """
        :return: if the application has additional information that can be shown to the user
        """
        pass

    @abstractmethod
    def can_be_downgraded(self):
        pass

    def can_be_uninstalled(self):
        return self.installed

    def can_be_installed(self):
        return not self.installed

    def is_update_ignored(self) -> bool:
        return False

    def supports_ignored_updates(self) -> bool:
        return False

    @abstractmethod
    def get_type(self):
        """
        :return: a string that represents the application type
        """
        pass

    @abstractmethod
    def get_default_icon_path(self):
        """
        :return: the path of a default icon when the application icon could not be retrieved (or will not be retrieved)
        """
        pass

    @abstractmethod
    def get_type_icon_path(self):
        """
            :return: the path of the application type icon
        """

    @abstractmethod
    def is_application(self):
        """
        :return: if the package is an application
        """
        pass

    def supports_disk_cache(self):
        """
        :return: if some application data and icon should be cached to the user disk
        """
        return self.installed and self.is_application()

    def get_disk_cache_path(self):
        """
        :return: base cache path for the specific app type
        """
        return f'{CACHE_DIR}/{self.get_type()}'

    def can_be_updated(self) -> bool:
        """
        :return: if the package can be updated.
        """
        return self.installed and self.update

    def get_disk_icon_path(self):
        path = self.get_disk_cache_path()
        if path:
            return '{}/icon.png'.format(path)

    def get_disk_data_path(self):
        path = self.get_disk_cache_path()
        if path:
            return '{}/data.json'.format(path)

    @abstractmethod
    def get_data_to_cache(self) -> dict:
        """
        :return: the application data that should be cached in disk / memory for quick access
        """
        pass

    @abstractmethod
    def fill_cached_data(self, data: dict):
        """
        sets cached data to the current instance
        :param data:
        :return:
        """
        pass

    @abstractmethod
    def can_be_run(self) -> bool:
        """
        :return: whether the app can be run via the GUI
        """

    def is_trustable(self) -> bool:
        """
        :return: if the package is distributed by a trustable source
        """
        return False

    @abstractmethod
    def get_publisher(self) -> str:
        """
        :return: the package publisher / maintainer
        """
        pass

    def get_custom_actions(self) -> Optional[Iterable[CustomSoftwareAction]]:
        """
        :return: custom supported actions
        """
        pass

    def has_screenshots(self) -> bool:
        """
        :return: if there are screenshots to be displayed
        """
        return not self.installed

    def get_name_tooltip(self) -> str:
        """
        :return: the application name that should be displayed on the UI tooltips.
        """
        return self.name

    def get_display_name(self) -> str:
        """
        :return: name displayed on the table
        """
        return self.name

    def get_update_tip(self) -> Optional[str]:
        """
        custom 'version' update tooltip
        """
        return

    @abstractmethod
    def supports_backup(self) -> bool:
        pass

    def __str__(self):
        return '{} (id={}, name={})'.format(self.__class__.__name__, self.id, self.name)


class PackageUpdate:

    def __init__(self, pkg_id: str, version: str, pkg_type: str, name: str):
        """
        :param pkg_id: an unique package identifier
        :param version: the new version
        :param pkg_type: the package type
        """
        self.id = pkg_id
        self.name = name
        self.version = version
        self.type = pkg_type

    def __str__(self):
        attrs = ', '.join(f'{p}={v}' for p, v in sorted(self.__dict__.items()))
        return f'{self.__class__.__name__} ({attrs})'

    def __eq__(self, other):
        if isinstance(other, PackageUpdate):
            return self.__dict__ == other.__dict__

        return False

    def __hash__(self):
        return sum(hash(v) for v in self.__dict__.values())


class PackageHistory:

    def __init__(self, pkg: SoftwarePackage, history: List[dict], pkg_status_idx: int):
        """
        :param pkg
        :param history: a list with the package history.
        :param pkg_status_idx: 'history' index in which the application is current found
        """
        self.pkg = pkg
        self.history = history
        self.pkg_status_idx = pkg_status_idx

    @classmethod
    def empyt(cls, pkg: SoftwarePackage):
        return cls(pkg=pkg, history=[], pkg_status_idx=-1)


class SuggestionPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    TOP = 3

    def __gt__(self, other):
        if isinstance(other, SuggestionPriority):
            return self.value > other.value

    def __lt__(self, other):
        if isinstance(other, SuggestionPriority):
            return self.value < other.value


class PackageSuggestion:

    def __init__(self, package: SoftwarePackage, priority: SuggestionPriority):
        self.package = package
        self.priority = priority
