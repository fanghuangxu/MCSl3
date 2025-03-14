import os




def find_addon(path):
    """
    path: str, 插件文件夹的路径
    return: list, 找到的插件名称列表
    """
    list_addon = []
    addons = os.listdir(path)
    for addon in addons:
        if str(addon).split(".")[-1] == "mel":
            list_addon.append(addon)
    return list_addon
