from module.iptables.config import config
import time
import threading
import os
import importlib
import globalvar as gVar
import os.path


def init():
    global hostmanager
    global stoping
    stoping = False
    hostmanager = gVar.get_value("modules")["hostmanager"]
    print("iptables init")


def start():
    global stoping
    stoping = False
    stoping
    sync()


def stop():
    global stoping
    stoping = True

# TODO wait for stoping


def inPrivate(hostname):
    hosts = os.listdir(__path__[0]+"/private/")
    for host in hosts:
        if host == hostname:
            return True
    return False


def sync():
    hostList = []
    # get all hosts
    for g in config["groups"]:
        for h in g["hosts"]:
            if h not in hostList:
                hostList.append(h)

    # 遍历主机
    for hostName in hostList:
        hostRules = ""
        tablesListCache = []
        # config["groups"].sort()  # TODO 按优先级排列
        # 遍历规则组
        for g in config["groups"]:
            # 查找主机是否在groups内
            if hostName in g["hosts"]:
                rulesPath = __path__[0]+"/groups/"+g["name"] + "/"  # 规则组文件夹
                if os.path.isdir(rulesPath):
                    tableList = os.listdir(rulesPath)
                    for tableName in tableList:  # 提取所有表 存入列表
                        if tableName not in tablesListCache:
                            tablesListCache.append(tableName)

        for tableName in tablesListCache:  # 遍历该主机拥有的表
            thisTable = ""
            # 再次遍历规则组
            for g in config["groups"]:
                # 查找主机是否在groups内
                if hostName in g["hosts"]:
                    # 表文件夹
                    tablePath = __path__[0]+"/groups/"+g["name"]+"/"+tableName
                    if os.path.isdir(tablePath):  # 表存在
                        # 添加
                        thisTable = genTable(tablePath)
            # head================
            # chain head
            thisTable = genChainsHeader(thisTable) + thisTable
            # table head
            thisTable = "*" + tableName + "\n" + thisTable
            # foot================
            thisTable += "COMMIT\n"
            hostRules += thisTable

        # TODO sync
        m_host = hostmanager.Host(hostName)
        opened = m_host.StartSSH()
        if opened:
            m_host.WriteFile(hostRules.encode("utf8"), "/tmp/iptables")
            stdin, stdout, stderr = m_host.Exec(
                "iptables-restore < /tmp/iptables")
            # print(stdout.read())
            m_host.StopSSH()
        else:
            # TODO log
            print("can not connect to \""+hostName+"\"")
    if not stoping:
        t = threading.Timer(config["interval"], sync)
        t.start()


def genPrivate(name):  # 生成private规则
    priTables = ""
    path = __path__[0]+"/private/"+name+"/"
    if os.path.isdir(path):
        tableNames = os.listdir(path)
        for tn in tableNames:
            priTables += genTable(path+tn)
    return priTables


def genTable(path):  # 根据文件夹内配置文件生成Table规则 不包含链头表头
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
        file = open(path+os.sep+name, mode="r", encoding="utf8")
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


depend = ["hostmanager"]
__all__ = ["depend", "init"]
