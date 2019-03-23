# servermanager

基于python3的服务器集群管理程序

# how to use

```
pip install paramiko
```

复制`config.py.default`到`config.py`并编辑

## Config
例子
```
config = {
    "module_disable": [
        "iptables", //要关闭的模块
    ],
    "log_level": 20,    //日志等级
    "log_path":"C:/Users/Lensual/servermanager/log" //日志路径
}
```

# Developer
## 主程序执行流程
1. server.py 入口
2. 初始化 globalvar 用于共享全局变量
3. 初始化 logger 并全局共享 logger 对象
4. 


## 模块开发说明