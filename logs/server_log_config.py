import logging.handlers
import os


SERVER_FORMATTER = logging.Formatter("%(asctime)s %(levelno)s %(module)s %(message)s")

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.ERROR)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)

LOG = logging.getLogger('server')
LOG.addHandler(STREAM_HANDLER)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='S'))


if __name__ == '__main__':
    LOG.debug('Debug information.')
    LOG.info('Important announcement.')
    LOG.warning('Warning!')
    LOG.error("Error!!!")
    LOG.critical('Critical error!')
