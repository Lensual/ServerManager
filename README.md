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
3. 初始化 logger
4. 初始化字典 modules 用于存储已加载的模块并全局共享
5. loadModules 导入`./module`里面所有的可用模块到 modules （自动处理依赖）
6. initModules 初始化所有 modules 里的模块
7. startModules 启动所有模块（TODO）
8. http启动监听


## 模块开发说明

所有模块在`./module`下建立文件夹

server.py中的模块加载过程
1. 读`./modules`下的文件夹，处理未启用的模块，处理依赖
    * **文件夹名作为模块名**
    * **依赖未找到则不加载**
    * 按依赖顺序深度优先递归加载
    * **请导出list类型的depend对象**
2. loadModules() 导入模块，存入全局的 modules
    * 导入模块用的方法是 importlib.import_module(moduleName)
    * **请使用globalvar的get_value("modules")获取modules**
3. initModules() 初始化 modules 中的模块
    * 调用的是模块中的init() **请导出此方法**
4. startModules() 启动 modules 中的模块 (TODO)
    * 调用的是模块中的start() ***请导出此方法**

### 关于模块接口导出
给`__all__`赋值即可导出接口

定义的公用接口

* depend: list类型，存模块名，用于依赖处理
* init: 模块的init方法
* start: 模块的start方法（TODO）


### 全局共享变量
globalvar提供了一个全局静态变量的支持

引用globalvar
> import globalvar as gVar

设置变量
>gVar.set_value(变量名,对象)

获取变量
>gVar.get_value(变量名)
