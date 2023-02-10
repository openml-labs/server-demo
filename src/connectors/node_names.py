import enum
from typing import Type


class NodeName(str, enum.Enum):
    example = "example"
    openml = "openml"
    huggingface = "huggingface"

    @staticmethod
    def from_class(clazz: Type):
        class_name = clazz.__name__  # E.g. OpenMlDatasetConnector
        name_parent = clazz.__base__.__name__  # E.g. DatasetConnector
        name = class_name.removesuffix(name_parent)
        return NodeName(name.lower())
