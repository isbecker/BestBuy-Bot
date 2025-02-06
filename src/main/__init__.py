import logging

from .bot import BotState, run
from .config import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main() -> int:
    try:
        run(config, BotState.PLACE_ORDER)
    except KeyboardInterrupt:
        logging.info("Exiting bot due to keyboard interrupt.")
        return 1
    return 0
