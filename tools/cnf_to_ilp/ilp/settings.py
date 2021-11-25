import enum


class GenerationMode(enum.Enum):
    certain = 1
    all = 2


GENERATION_MODE = GenerationMode.all
GENERATION_BACKDOOR_VALUES_COUNT = 1
