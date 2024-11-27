import logging

logging.basicConfig(level=logging.INFO, format="ts=%(asctime)s level=%(levelname)s message=%(message)s")


# TODO: Improve logging
def log(message):
    logging.info(msg=message)


def log_debug(message):
    logging.debug(msg=message)


def log_error(message):
    logging.error(msg=message)
