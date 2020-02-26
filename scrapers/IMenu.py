from abc import ABC, abstractmethod


class IMenu(ABC):
    @abstractmethod
    def get_todays_menu(self) -> dict:
        raise NotImplementedError
