import logging

from sages.configs import configs

logging.basicConfig(level=configs.log_level)
sage_logger = logging.getLogger("OpsSage")
