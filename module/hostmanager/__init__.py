from module.hostmanager.config import config
import paramiko
import time


def init():
    pass


def getHosts():
    return config["hosts"]


class Host:
    __Terminal = None

    def __init__(self, name):
        for host in config["hosts"]:
            if host["name"] == name:
                self.__hostconf = host
                break
        if self.__hostconf is None:
            raise Exception

    def StartTerminal(self):
        if self.__Terminal is not None:
            return True
        else:
            try:
                sshconf = self.__hostconf["ssh"]
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
                #TODO private key login
                #TODO ssh.get_host_keys().add(self.__hostconf["ip"], 'ssh-rsa', key)
                ssh.connect(self.__hostconf["ip"],
                            username=sshconf["username"],
                            password=sshconf["password"],
                            port=sshconf["port"])
                self.__Terminal = ssh.invoke_shell()
                return True
            except:
                raise

    def SetTimeout(self, timeout):
        if self.__Terminal is not None:
            self.__Terminal.settimeout(timeout)
            return True
        else:
            return False

    def StopTerminal(self):
        if self.__Terminal is None:
            self.__Terminal.close()
        return True

    def Term_Readline(self, timeout=20):
        line = ""
        seconds = 0
        while True:
            if self.__Terminal.recv_ready():
                seconds = 0
                buffer = self.__Terminal.recv(1)
                if buffer == "":  # channel closed
                    raise Exception("channel closed")
                line += buffer.decode("utf8")
                if line[-1] == "\n":
                    break
            else:
                # Timer
                time.sleep(0.01)  # 10ms
                seconds += 0.01
                if seconds >= timeout:
                    raise Exception("read timeout")
        return line

    def Term_Read(self, length, timeout=20):
        buffer = self.__Terminal.recv(length)
        return buffer

    def Term_ReadStr(self, length, timeout=20):
        buffer = self.__Terminal.recv(length)
        return buffer.decode("utf8")

#TODO 传文件

    def SendFile(self,filepath,savepath):
        pass

    def RecvFile(self,filepath,savepath):
        pass

    def WriteFile(self,bytes,filepath):
        pass

    def ReadFile(self,filepath):
        pass

#TODO 执行命令

    def Exec(self,cmd):
        pass

__all__ = ["init"]
