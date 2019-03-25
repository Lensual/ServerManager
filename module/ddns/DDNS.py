import json
import os
import time

import urllib3

import logger


class DDNS_Interface():
    supported = ["Cloudflare"]
    @staticmethod
    def Cloudflare(Cloudflare_list, new_ipv4, new_ipv6):
        for user in Cloudflare_list.keys():
            user = Cloudflare_list[user]
            cf = Cloudflare(user["email"], user["api_key"])
            for domain in user["domains"].keys():
                domain = user["domains"][domain]
                if domain["type"] == "A":
                    new_ip = new_ipv4
                elif domain["type"] == "AAAA":
                    new_ip = new_ipv6
                if domain["enable"] == True:
                    cf.update_DNS_Record(
                        domain["prefix"], domain["domain"], new_ip, domain["type"])


class IPv6_Toolkit():
    @staticmethod
    def get_IPv6_Prefix_by_Route():  # 通过路由表获取前缀
        getprefix = os.popen("route -A inet6 -n|grep ::/64|grep -v fe80::/64")
        prefix = getprefix.read().split("/")[0]
        logger.info("Get IPv6 prefix by route:"+prefix)
        return prefix

    @staticmethod
    def get_IPv6_Addr_by_DefaultRoute():  # 通过默认路由获取/128地址
        getip = os.popen(
            "route -A inet6 -n|grep /128|grep -v fe80::|grep -v ::1/128")
        ip = getip.read().split("/")[0]
        logger.info("Get IPv6 address by route:"+ip)
        return ip

    @staticmethod
    def get_IPv6_Addr_by_Site():
        getip = os.popen("curl -k -s checkipv6.dyndns.com")
        ip = getip.read().split(": ")[1].split("<")[0]
        logger.info("Get IPv6 address by site:"+ip)
        return ip


class IPv4_Toolkit():
    @staticmethod
    def get_IPv4_Addr_by_ifconfig():
        getip = os.popen("ifconfig |grep inet|grep -v inet6|grep -v 127.0.0.1")
        ip = getip.read().split("inet")[1].split(" ")[1]
        logger.info("Get IPv6 address by ifconfig:"+ip)
        return ip

    @staticmethod
    def get_IPv4_Addr_by_Site_oray():
        getip = os.popen("curl -k -s ddns.oray.com/checkip")
        ip = getip.read().split("Current IP Address: ")[1].split("<")[0]
        logger.info("Get IPv4 address by site:"+ip)
        return ip

    @staticmethod
    def get_IPv4_Addr_by_Site_AWS():
        getip = os.popen("curl -k -s http://checkip.amazonaws.com")
        ip = getip.read()
        logger.info("Get IPv4 ddress by site:"+ip)
        return ip


class Cloudflare():

    def __init__(self, email, key):
        self.api_email = email
        self.api_key = key
        self.zone_id = {}  # zone_id={domain:id}
        self.get_ZoneID()
        self.record_id = {}  # record_id={domain:[{id,type,name,content}]}
        self.get_RecordID()
        self.headers = {'X-Auth-Email': email,
                        'X-Auth-Key': key, 'Content-Type': 'application/json'}

    def __get_request__(self, url):
        # 返回json的string
        r = urllib3.PoolManager().request("GET", url, headers=self.headers).data
        r = str(r, encoding="utf-8")
        return r

    def __put_request__(self, url, data):
        # data为一个字典
        data = json.dumps(data).encode('utf-8')
        r = urllib3.PoolManager().request("PUT", url, body=data, headers=self.headers).data
        r = str(r, encoding="utf-8")
        return r

    def update_DNS_Record(self, prefix, domain, new_content, type):
        if not (prefix == "@" or prefix == ""):
            name = prefix+"."+domain
        else:
            name = domain
        zoneid = self.zone_id[domain]

        recordid = ""
        for record in self.record_id[domain]:
            if record["type"] == type and record["name"] == name:  # 如果找到已存在的匹配项
                recordid = record["id"]
                if record["content"] == new_content:  # 如果值没有变化
                    logger.info(name+" IP no change")
                    return
                else:
                    break
        if recordid == "":  # 找不到则新建记录
            logger.error("Can't find record!")
            None
        data = {"type": type, "name": name, "content": new_content}
        updaterecord = self.__put_request__(
            "https://api.cloudflare.com/client/v4/zones/"+zoneid+"/dns_records/"+recordid, data)
        result = json.loads(updaterecord)
        if result["success"]:
            logger.info("Successfully Update DNS record of "+name +
                        ", from "+record["content"]+" to "+new_content)
        else:
            logger.error("Update DNS record of "+name+" failed! Error+" +
                         result["errors"]["code"]+":"+result["errors"]["message"])

    # TODO 新建一条记录(type prefix,domain,content,ttl=120)

    def get_ZoneID(self):
        getzone = self.__get_request__(
            "https://api.cloudflare.com/client/v4/zones")
        domain_list = json.loads(getzone)["result"]
        for domain in domain_list:
            self.zone_id[domain["name"]] = domain["id"]

    def get_RecordID(self):
        for domain in self.zone_id.keys():
            self.record_id[domain] = []
            getrecord = self.__get_request__(
                "https://api.cloudflare.com/client/v4/zones/"+self.zone_id[domain]+"/dns_records")
            record_list = json.loads(getrecord)["result"]
            for record in record_list:
                self.record_id[domain].append(
                    {"name": record["name"], "id": record["id"], "type": record["type"], "content": record["content"]})
