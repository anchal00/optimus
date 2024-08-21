import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# TODO: Improve logging
def log(message):
    logging.info(msg=message)


def log_error(message):
    logging.error(msg=message)
