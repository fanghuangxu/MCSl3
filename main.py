import os
import tkinter as tk
import McslLibs
import McslLibs.addon
import McslLibs.addon.find
import McslLibs.addon.load



root = tk.Tk()
root.geometry("500x300")

# 寻找插件
addon_path = os.path.join(os.path.dirname(__file__), ".MCSL3/addons")
addons = McslLibs.addon.find.find_addon(addon_path)
addon_temp_path = os.path.join(os.path.dirname(__file__), ".MCSL3/AddonsTemp")

# 初始化temp文件夹

os.system("rm -rf "+os.path.join(os.path.dirname(__file__), ".MCSL3/AddonsTemp"))


# 加载插件

extractall_status = McslLibs.addon.load.extractall_addons(addon_path,os.path.join(os.path.dirname(__file__), ".MCSL3/AddonsTemp"),addons)
print(extractall_status)

print(addon_temp_path,addons)


#添加插件入口
for addon in addons:
    McslLibs.addon.load.add_buttons(root,addon_temp_path,addon)


root.mainloop()

