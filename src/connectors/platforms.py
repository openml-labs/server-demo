import enum
from typing import Type


class Platform(str, enum.Enum):
    example = "example"
    openml = "openml"
    huggingface = "huggingface"

    @staticmethod
    def from_class(clazz: Type):
        class_name = clazz.__name__  # E.g. OpenMlDatasetConnector
        name_parent = clazz.__base__.__name__  # E.g. DatasetConnector
        platform_name = class_name.removesuffix(name_parent)
        return Platform(platform_name.lower())
