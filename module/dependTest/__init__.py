import logger
depend = ["helloworld"]

def init():
    logger.warn("dependTest inited. Please Delete This Module.")

__all__ = ["depend","init"]