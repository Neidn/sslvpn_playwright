import os
import logging

# LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOG_DIR, "action.log")
LOG_BACKUP_COUNT = 7


def init_log() -> logging:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=LOG_FILE,
        filemode='a'
    )

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    return logging


# Usage
"""
if __name__ == '__main__':
    logger = init_log()
    logger.info('test')
    logger.error('test')
    logger.warning('test')
    logger.debug('test')
"""
