import threading
from datetime import datetime
from time import sleep

import logger
from ddns.config import *
from ddns.DDNS import *

thread_flag = 0  # 线程锁，标记一次DDNS过程是否结束
stop_flag = 0  # 是否stop

thread_flag = 0  # 标志是否可以stop线程


def init():
    logger.info("ddns inited")


def do():
    global thread_flag
    thread_flag = 1
    new_ipv4 = IPv4_Toolkit.get_IPv4_Addr_by_Site_oray()
    new_ipv6 = IPv6_Toolkit.get_IPv6_Addr_by_Site()
    for DDNS_SP in config.keys():
        if DDNS_SP in DDNS_Interface.supported:
            args = [config[DDNS_SP], new_ipv4, new_ipv6]
            getattr(DDNS_Interface, DDNS_SP)(*args)
    logger.info("DDNS waiting for next update, "+span+" seconds left...")
    thread_flag = 0


def daemon():
    while(True):
        do()
        a = datetime.now()
        while(True):
            b = datetime.now()
            if(stop_flag == 1):
                return
            if((b-a).seconds == span):
                break


def start():
    global t
    print("DDNS started")
    t = threading.Thread(target=daemon)
    t.start()


def stop():
    global thread_flag, stop_flag
    stop_flag = 1
    if(thread_flag == 1):
        print("Waiting for DDNS thread done...")
        while(thread_flag == 1):
            None
    print("DDNS stopped")


def restart():
    stop()
    start()
    print("DDNS restarted")
