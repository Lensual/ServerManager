from iptables.config import config
import time
import threading
import os
import importlib
import globalvar as gVar
import os.path
import logger


def init():
    global hostmanager
    global stoping
    stoping = False
    hostmanager = gVar.get_value("modules")["hostmanager"]
    logger.info("iptables inited")


def start():
    global stoping
    stoping = False
    sync()


def stop():
    global stoping
    stoping = True

# TODO wait for stoping


def sync():
    # get all hosts
    hostsDir = __path__[0]+"/hosts/"
    if os.path.isdir(hostsDir):
        hostList = []
        hostsPath = os.listdir(hostsDir)
        for p in hostsPath:
            if os.path.splitext(p)[1] == ".conf":
                name = os.path.splitext(os.path.basename(p))[0]
                if hostmanager.inManaged(name):
                    hostList.append({"name": name, "path": hostsDir+p})

    for host in hostList:
        logger.debug("Host: "+host["name"])
        rules = makeRules(host["path"])
        logger.debug("Rules: \n"+rules)
        manager = hostmanager.Host(host["name"])
        opened = manager.StartSSH()
        if opened:
            manager.WriteFile(rules.encode("utf8"), "/tmp/iptables")
            stdin, stdout, stderr = manager.Exec(
                "iptables-restore < /tmp/iptables")
            manager.StopSSH()
            # TODO stdout
        else:
            logger.error("can not connect to \""+host["name"]+"\"")

    if not stoping:
        t = threading.Timer(config["interval"], sync)
        t.start()

    logger.info("iptables同步完成")


def makeRules(path):  # 生成规则
    rules = ""
    file = open(path, mode="r", encoding="utf-8")
    lines = file.readlines()

    for line in lines:
        if not notRule(line):
            # 表达式
            while True:
                found = False
                matched = False
                exp = ""
                for char in line:
                    if char == "{":
                        matched = True
                        found = True
                    elif char == "}":
                        matched = False
                        expArgs = exp.split(",")
                        line = line.replace("{"+exp+"}", parseExp(expArgs))
                        break
                    if matched and char != "{":
                        exp += char
                if not found:
                    break
        rules += line

    return rules


def parseExp(args):
    path = __path__[0]+"/rules/"+args[0]
    if os.path.isfile(path):
        file = open(path, mode="r", encoding="utf-8")
        txt = file.read()
        file.close()
        return txt
    else:
        # TODO err
        pass
    # TODO 其他表达式


def notRule(rule):  # 判断注释与空行
    if rule.strip() == "":
        return True
    if rule.strip()[0] == "#":
        return True
    return False


# def getChainFromRule(rule):  # 从单句规则里面取-A后面的链名
#     chain = ""
#     arr = rule.split("-A")
#     inCopy = False
#     for char in arr[1]:
#         if char != " ":
#             inCopy = True
#             chain += char
#         elif inCopy:
#             break
#     return chain


depend = ["hostmanager"]
__all__ = ["depend", "init"]
