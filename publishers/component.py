from __future__ import annotations

from abc import ABC, abstractmethod

from .update import UpdateStatus


class Component(ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @abstractmethod
    def check_for_updates(self) -> UpdateStatus:
        raise NotImplementedError("TODO")
