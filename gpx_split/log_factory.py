import logging

class LogFactory:

    def create(name):
        #create logger
        logger = logging.getLogger(name)

        # create console handler with a debug log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('- %(name)s - %(levelname)-8s: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger