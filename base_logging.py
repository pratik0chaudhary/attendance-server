import logging
import os

from main.settings import BASE_DIR
filepath = os.path.join(
    os.path.dirname(
        os.path.abspath(
            BASE_DIR
        )
    ),
    'sync.log'
)

bare_format = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.FileHandler(filename=filepath)
stream_handler = logging.StreamHandler()
file_handler.setFormatter(bare_format)
stream_handler.setFormatter(bare_format)

logger = logging.getLogger(__file__)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel('DEBUG')
