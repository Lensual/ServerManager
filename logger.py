import logging
import logging.handlers
import os
import inspect


def _init(config):
    global logger

    # logger init
    if config["log_level"] is None:
        config["log_level"] = logging.NOTSET

    fmt = '%(asctime)s [%(levelname)s]: %(message)s'

    #stdout
    logging.basicConfig(level=config["log_level"],
                        format=fmt)
    logger = logging.getLogger()

    #logfile
    os.makedirs(config["log_path"], 755, True)
    logHandler = logging.handlers.TimedRotatingFileHandler(
        config["log_path"]+os.sep+"servermanager", "midnight")
    logHandler.suffix = "%Y%m%d-%H%M.log"
    logHandler.setFormatter(logging.Formatter(fmt))
    logHandler.setLevel(config["log_level"])

    logger.addHandler(logHandler)


def debug(msg):
    logger.debug("["+__getCaller()+"] "+msg)


def info(msg):
    logger.info("["+__getCaller()+"] "+msg)


def warn(msg):
    logger.warn("["+__getCaller()+"] "+msg)


def error(msg):
    logger.error("["+__getCaller()+"] "+msg)


def __getCaller():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    return inspect.getmodule(calframe[2][0]).__name__
