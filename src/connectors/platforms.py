import enum


class Platform(str, enum.Enum):
    example = "example"
    openml = "openml"
    huggingface = "huggingface"
