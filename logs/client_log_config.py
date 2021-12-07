import logging
import os
import sys

sys.path.append('../')

CLIENT_FORMATTER = logging.Formatter("%(asctime)s %(levelno)s %(module)s %(message)s")

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.ERROR)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)

LOG = logging.getLogger('client')
LOG.addHandler(STREAM_HANDLER)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.FileHandler(PATH, encoding='utf-8'))


if __name__ == '__main__':
    LOG.debug('Debug information.')
    LOG.info('Important announcement.')
    LOG.warning('Warning!')
    LOG.error("Error!!!")
    LOG.critical('Critical error!')
