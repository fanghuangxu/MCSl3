import tkinter as tk
import zipfile
import os
import json
import importlib




# 给插件调用的函数 start：
import tkinter as tk
from tkinter import messagebox
def clear(window):

    for widget in window.winfo_children():
        if not isinstance(widget, tk.Menu):  # 检查是否为菜单
            widget.destroy()  # 销毁控件
def run_bash(command:str):
    os.system(command)



# 给插件调用的函数 end


def extractall_addons(path,path2,addons):
    """
    加载插件
    path: str,插件目录
    path2:str,MCSL临时文件夹
    addons: str,要加载的插件列表
    window: tkinter窗口对象
    return: {"status":"1","msg":"加载成功"} or {"status":"0","msg":"加载失败,<error_msg>"}
    """
    try:
        # 解压插件报至MCSL临时文件夹
        print(addons)
        for addon in addons:
            print("正在加载插件："+addon)
            print("插件加载中 path:",os.path.join(path, addon)," -> ",os.path.join(path2, addon.split(".")[0]))
            if not os.path.exists(os.path.join(path2, addon.split(".")[0])):
                os.makedirs(os.path.join(path2, addon.split(".")[0]))
            with zipfile.ZipFile(os.path.join(path, addon), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(path2, addon.split(".")[0]))
            
    except Exception as e:
        return {"status": "0", "msg": "加载失败," + str(e)}
    

def load_addons(window,addons_path):
    """
    运行插件
    window: tkinter窗口对象
    addons_path: str,插件目录
    """
    with open(f"{addons_path}/addonConfig.json") as config_file:
        config_=json.load(config_file)
    orgin=config_["orgin"]
    name=config_["name"]
    print("运行插件",name)
    with open(f"{addons_path}/{orgin}/main.py") as code_file:
        code=code_file.read()
    exec(code,globals())

    # 获取插件配置

    main_func=config["main"] # type: ignore
    main(window) # type: ignore

def add_buttons(window,path,addon):
    """
    添加按钮
    window: tkinter窗口对象
    path: str,插件目录
    addon: str,要加载的插件
    """
    path=os.path.join(path, addon.split(".")[0])
    with open(f"{path}/{addon.split('.')[0]}/addonConfig.json","r") as f:
        config=json.loads(f.read())
    """menu_bar=tk.Menu(window)
    name=config["name"]
    menu_bar.add_command(label=name,command=lambda:print(name))"""
    tk.Button(window,text=config["name"],command=lambda:load_addons(window,f"{path}/{addon.split('.')[0]}")).pack()







"""
echo "# MCSl3" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:fanghuangxu/MCSl3.git
git push -u origin main
"""
