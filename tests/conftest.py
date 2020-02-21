import enum
import logging

import colorlog
import pytest

logger = logging.getLogger(__name__)
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "(%(asctime)s) [%(log_color)s%(levelname)s] | %(name)s | %(message)s [%(threadName)-10s]"
    )
)

# get root logger and add handler
logger = logging.getLogger()
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class FruitEnum(enum.Enum):
    ORANGE = enum.auto()
    APPLE = enum.auto()
    PEAR = enum.auto()
    BANANA = enum.auto()


@pytest.fixture
def Fruit():
    return FruitEnum
