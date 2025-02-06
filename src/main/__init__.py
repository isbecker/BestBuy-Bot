import logging

from .bot import BotState, run
from .config import config

log_level = getattr(logging, config.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")


def obfuscate_sensitive_data(config):
    obfuscated_config = config.copy()
    obfuscated_config.email = "****@****.com"
    obfuscated_config.password = "********"
    obfuscated_config.cvv = "***"
    return obfuscated_config


def main() -> int:
    logging.info("Starting bot.")
    try:
        if log_level == logging.DEBUG:
            logging.debug(f"Current configuration: {config}")
        else:
            logging.info(f"Current configuration: {obfuscate_sensitive_data(config)}")
        run(config, BotState.COMPLETE)
    except KeyboardInterrupt:
        logging.info("Exiting bot due to keyboard interrupt.")
        return 1
    return 0
