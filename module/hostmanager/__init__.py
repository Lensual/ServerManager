from module.hostmanager.config import config
import paramiko
import time
import base64
from io import StringIO

# TODO err catch and log


def init():
    print("hostmanager init")


def getHosts():
    hosts = []
    for host in config["hosts"]:
        hosts.append({"name": host["name"], "ip": host["ip"]})
    return hosts


def inManaged(hostname):
    for host in config["hosts"]:
        if host["name"] == hostname:
            return True
    return False


class Host:
    __Terminal = None
    __ssh = None
    __hostconf = None

    def __init__(self, name):
        for host in config["hosts"]:
            if host["name"] == name:
                self.__hostconf = host
                break
        if self.__hostconf is None:
            raise Exception

    def StartSSH(self):
        if self.__ssh is None:
            try:
                sshconf = self.__hostconf["ssh"]
                self.__ssh = paramiko.SSHClient()
                self.__ssh.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy)
                # TODO ssh.get_host_keys().add(self.__hostconf["ip"], 'ssh-rsa', key)
                if sshconf["prikey"] is not None:
                    pkey = paramiko.RSAKey.from_private_key(
                        StringIO(sshconf["prikey"]))
                    self.__ssh.connect(self.__hostconf["ip"],
                                       username=sshconf["username"],
                                       port=sshconf["port"],
                                       pkey=pkey,
                                       passphrase=sshconf["passphrase"])
                else:
                    self.__ssh.connect(self.__hostconf["ip"],
                                       username=sshconf["username"],
                                       password=sshconf["password"],
                                       port=sshconf["port"])

            except TimeoutError:
                self.clean()
                return False
            except:
                self.clean()
                raise

        return True

    def clean(self):
        if  self.__Terminal is not None:
            self.__Terminal.close()
            del self.__Terminal
        if self.__ssh is not None:
            self.__ssh.close()
            del self.__ssh


    def StopSSH(self):
        if self.__ssh is not None:
            self.__ssh.close()
            del self.__ssh
        return True

    def StartTerminal(self):
        if self.__Terminal is None:
            try:
                self.StartSSH()
                self.__Terminal = self.__ssh.invoke_shell()
                self.__Terminal.set_combine_stderr(True)
                return True
            except:
                raise
        return True

    def StopTerminal(self):
        if self.__Terminal is not None:
            self.__Terminal.close()
            del self.__Terminal
        return True

    def SetTimeout(self, timeout):
        if self.__Terminal is not None:
            self.__Terminal.settimeout(timeout)
            return True
        else:
            return False

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

    def Exec(self, cmd):
        return self.__ssh.exec_command(cmd)

    def SendFile(self, localpath, remotepath):
        sftp = self.__ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close

    def RecvFile(self, remotepath, localpath):
        sftp = self.__ssh.open_sftp()
        sftp.get(remotepath, localpath)
        sftp.close()

    def WriteFile(self, data, remotepath):
        sftp = self.__ssh.open_sftp()
        file = sftp.open(remotepath, "wb")
        file.set_pipelined()
        file.write(data)
        file.flush()
        file.close()
        sftp.close()

    def ReadFile(self, remotepath, length):
        sftp = self.__ssh.open_sftp()
        file = sftp.open(remotepath, "rb")
        buffer = file.read()
        file.close()
        sftp.close()
        return buffer


__all__ = ["init"]
