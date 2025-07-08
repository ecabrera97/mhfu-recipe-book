import logging


formatter = logging.Formatter('%(levelname)s->\t%(filename)s-%(lineno)d: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers = [handler]