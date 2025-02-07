from loguru import logger

from .bot import BotState, run
from .config import config

log_level = config.log_level.upper()
logger.remove()
logger.add(lambda msg: print(msg, end=""), level=log_level, colorize=True)


def obfuscate_sensitive_data(config):
    obfuscated_config = config.copy()
    obfuscated_config.email = "****@****.com"
    obfuscated_config.password = "********"
    obfuscated_config.cvv = "***"
    return obfuscated_config


@logger.catch
def main() -> int:
    logger.info("Starting bot.")
    try:
        if log_level == "DEBUG":
            logger.debug(f"Current configuration: {config}")
        else:
            logger.info(f"Current configuration: {obfuscate_sensitive_data(config)}")
        run(config, BotState.COMPLETE)
    except KeyboardInterrupt:
        logger.info("Exiting bot due to keyboard interrupt.")
        return 1
    return 0
