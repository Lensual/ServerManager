#!/usr/bin/python3
import sys
import os
import os.path
import importlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import logging.handlers
import globalvar as gVar
gVar._init()

from config import config

import logger
logger._init(config)
logger.debug("logger inited")

# Modules
modules = {}
gVar.set_value("modules", modules)
modDir = []
sys.path.append("./module")



def loadModules():
    global modDir
    modDir = os.listdir("./module")
    for moduleName in modDir:
        if moduleName not in config["module_disable"]: # 不初始化disable列表里的
            loadModule(moduleName)


def loadModule(moduleName):
    global modDir
    global modules

    m = importlib.import_module(moduleName)

    # 已存在
    if existModule(moduleName):
        return False
    # 处理依赖
    if "depend" in dir(m) and len(m.depend) > 0:
        for depName in m.depend:
            # 文件查找
            if depName not in modDir:
                logger.error(
                    "module \"{depName}\" not found".format_map(vars()))
                return False

            # 排除配置disable
            if depName in config["module_disable"]:
                logger.warn(
                    "module \"{m.__name__}\" depend on \"{depName}\", but it's disabled".format_map(vars()))
                return False

            # log out
            logger.info(
                "module \"{m.__name__}\" depend on \"{depName}\"".format_map(vars()))

            # 跳过已加载的模块
            if existModule(depName):
                logger.debug("module \"{depName}\" exist. skip".format_map(vars()))
                continue

            # 递归加载依赖
            success = loadModule(depName)
            if not success:
                # TODO err out
                logger.warn("module \""+depName+"\" exist")
                return False
    # 正常加载
    modules[moduleName] = m
    logger.info("load module \"{m.__name__}\"".format_map(vars()))
    return True


def existModule(moduleName):
    global modules
    if moduleName in modules:
        return True
    else:
        return False


def initModules():
    global modules
    for mName in modules:
        modules[mName].init()


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split(os.sep)
        print(path)
        BaseHTTPRequestHandler.send_response(self, 200, "hello")

    def do_POST(self):
        pass


logger.debug("loading modules")
loadModules()
logger.debug("modules load complete")
logger.debug("initializing modules")
initModules()
logger.debug("modules initialize complete")

# debug
modules["iptables"].start()

# http
httpd = HTTPServer(("", 5000), RequestHandler)
httpd.serve_forever()
