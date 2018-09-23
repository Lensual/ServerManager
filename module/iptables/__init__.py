from module.iptables.config import config
import time
import threading
import os
import importlib


def init():
    sync()


def start():
    t = threading.Timer(config["interval"], sync)
    t.start()


def stop():
    pass


def sync():
    # scan global rules
    gTables = []
    gTableNames = os.listdir(__path__[0]+"/global/")
    for gTableName in gTableNames:
        gTables.append({"name": gTableName, "gTable": genTable(
            __path__[0]+"/global/"+gTableName)})

    # scan private rules
    pHosts = os.listdir(__path__[0]+"/private/")
    for host in config["hosts"]:
        for pHost in pHosts:
            if host["name"] == pHost:
                hostRules = ""
                # Tables scan and merge
                pTableNames = os.listdir(__path__[0]+"/private/"+pHost)
                for pTableName in pTableNames:
                    tableRules = ""
                    # private rules
                    tableRules += genTable(__path__[0]+"/global/"+pTableName)
                    for gTable in gTables:
                        if gTable["name"] == pTableName:
                            tableRules += gTable["gTable"]  # global rules
                    # head=====================
                    # chains
                    tableRules = genChainsHeader(tableRules)+tableRules
                    # table name
                    tableRules = "*"+pTableName+"\n"+tableRules
                    # foot=====================
                    tableRules += "COMMIT\n"
                    hostRules += tableRules
                # add global
                for gTable in gTables:
                    exist = False
                    for pTableName in pTableNames:
                        if gTable["name"] == pTableName:
                            exist = True
                            break
                    if not exist:
                        tableRules = gTable["gTable"]
                        # head================
                        # chains
                        tableRules = genChainsHeader(tableRules)+tableRules
                        # table name
                        tableRules = "*"+gTable["name"]+"\n"+tableRules
                        # foot================
                        tableRules += "COMMIT\n"
                        hostRules += tableRules
                # TODO sync
                print(hostRules)
                print("\n\n\n\n\n\n\n")


def genPrivate(name):  # 生成private规则
    priTables = ""
    path = __path__[0]+"/private/"+name+"/"
    if os.path.isdir(path):
        tableNames = os.listdir(path)
        for tn in tableNames:
            priTables += genTable(path+tn)
    return priTables


def genTable(path):  # 根据文件夹内配置文件生成Table规则
    table = ""

    # rules===============
    fNames = os.listdir(path)
    # 过滤扩展名
    for i in range(len(fNames)):
        if os.path.splitext(fNames[i])[-1][1:] != "conf":
            del fNames[i]
            i -= 1

    # 排序
    fNames.sort()

    # 读
    fileText = ""
    for name in fNames:
        # TODO 自动生成注释和容错
        file = open(path+os.sep+name, mode="r")
        fileText += file.read()
        file.close()
        fileText += "\n"
    table += fileText

    return table


def genChainsHeader(rules):  # 生成表头 链声明
    header = ""
    chains = []
    lines = rules.splitlines()
    for line in lines:
        if not notRule(line):
            chain = getChainFromRule(line)
            if chain not in chains:
                chains.append(chain)
    for chain in chains:
        # TODO custom policy
        # TODO 数据包统计
        header = ":"+chain+" - [0:0]\n"+header

    return header


def notRule(rule):  # 判断注释与空行
    if rule.strip() == "":
        return True
    if rule.strip()[0] == "#":
        return True
    return False


def getChainFromRule(rule):  # 从单句规则里面取-A后面的链名
    chain = ""
    arr = rule.split("-A")
    inCopy = False
    for char in arr[1]:
        if char != " ":
            inCopy = True
            chain += char
        elif inCopy:
            break
    return chain


__all__ = ["init"]