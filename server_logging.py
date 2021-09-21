import logging


def init_logger():
    logger = logging.getLogger('mclite_server')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s > %(name)s > %(levelname)s > %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


class ConnectionLogAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """

    def process(self, msg, kwargs):
        return '[%s:%s] %s' % (self.extra['client_host'], self.extra['client_port'], msg), kwargs
