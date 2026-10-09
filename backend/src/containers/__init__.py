"""Dependency injection containers. Routers resolve use cases from `container`."""

from src.containers.root import RootContainer

container = RootContainer()

__all__ = ["container"]
