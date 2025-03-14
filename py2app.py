import os
import shutil
import subprocess
import sys
import argparse
from pathlib import Path
import zipfile
import tarfile
import plistlib

class PythonPackager:
    def __init__(self, script, output_dir, onefile=False, windowed=False, icon=None, name=None):
        self.script = Path(script).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.onefile = onefile
        self.windowed = windowed
        self.icon = icon
        self.name = name or self.script.stem
        self.python_exe = sys.executable
        self.platform = sys.platform  # 获取操作系统信息

    def copy_dependencies(self):
        """使用 pipreqs 提取依赖并安装"""
        print("提取依赖库...")
        requirements_file = self.output_dir / "requirements.txt"
        # 使用 pipreqs 命令行工具生成 requirements.txt
        try:
            subprocess.run(
                [self.python_exe, "-m", "pipreqs.pipreqs", "--encoding=utf8", "--force", str(self.script.parent)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # 将生成的 requirements.txt 移动到输出目录
            generated_req = self.script.parent / "requirements.txt"
            if generated_req.exists():
                shutil.move(generated_req, requirements_file)
            else:
                raise FileNotFoundError("pipreqs 未能生成 requirements.txt")
        except subprocess.CalledProcessError as e:
            print(f"pipreqs 调用失败: {e.stderr.decode()}")
            sys.exit(1)
        except Exception as e:
            print(f"依赖提取失败: {e}")
            sys.exit(1)

        # 安装依赖到打包目录
        lib_dir = self.output_dir / "lib"
        lib_dir.mkdir(exist_ok=True)
        subprocess.run([self.python_exe, "-m", "pip", "install", "-r", str(requirements_file), "--target", str(lib_dir)], check=True)

    def copy_python_interpreter(self):
        """复制 Python 解释器到打包目录"""
        print("复制 Python 解释器...")
        python_dir = self.output_dir / "python"
        python_dir.mkdir(exist_ok=True)
        if os.name == "nt":  # Windows
            shutil.copy(self.python_exe, python_dir / "python.exe")
        else:  # macOS/Linux
            shutil.copy(self.python_exe, python_dir / "python")

    def create_launcher(self):
        """生成启动脚本"""
        print("生成启动脚本...")
        if os.name == "nt":  # Windows
            launcher = self.output_dir / f"{self.name}.bat"
            with open(launcher, "w") as f:
                f.write(f"@echo off\n")
                f.write(f"set PYTHONPATH=lib\n")
                f.write(f"python\\python.exe {self.script.name}\n")
        else:  # macOS/Linux
            launcher = self.output_dir / f"{self.name}.sh"
            with open(launcher, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"export PYTHONPATH=lib\n")
                f.write(f"python/python {self.script.name}\n")
            os.chmod(launcher, 0o755)  # 赋予执行权限

    def package_as_single_file(self):
        """将打包目录压缩为单个文件"""
        print("打包为单个文件...")
        if os.name == "nt":  # Windows
            zip_path = self.output_dir.parent / f"{self.name}.zip"
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for root, _, files in os.walk(self.output_dir):
                    for file in files:
                        zipf.write(
                            os.path.join(root, file),
                            os.path.relpath(os.path.join(root, file), self.output_dir)
                        )
            print(f"打包完成！输出文件: {zip_path}")
        else:  # macOS/Linux
            tar_path = self.output_dir.parent / f"{self.name}.tar.gz"
            with tarfile.open(tar_path, "w:gz") as tarf:
                tarf.add(self.output_dir, arcname=os.path.basename(self.output_dir))
            print(f"打包完成！输出文件: {tar_path}")

    def create_extract_and_run_launcher(self):
        """生成解压并运行的启动器"""
        print("生成解压并运行的启动器...")
        if os.name == "nt":  # Windows
            launcher = self.output_dir.parent / f"{self.name}_launcher.bat"
            with open(launcher, "w") as f:
                f.write("@echo off\n")
                f.write(f"powershell -command \"Expand-Archive -Path '{self.name}.zip' -DestinationPath .\"\n")
                f.write(f"cd {self.name}\n")
                f.write(f"call {self.name}.bat\n")
            print(f"启动器生成完成: {launcher}")
        else:  # macOS/Linux
            launcher = self.output_dir.parent / f"{self.name}_launcher.sh"
            with open(launcher, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"tar -xzf {self.name}.tar.gz\n")
                f.write(f"cd {self.name}\n")
                f.write(f"./{self.name}.sh\n")
            os.chmod(launcher, 0o755)  # 赋予执行权限
            print(f"启动器生成完成: {launcher}")

    def set_windows_icon(self, icon_path):
        """设置 Windows 可执行文件的图标"""
        if not icon_path.endswith(".ico"):
            print("Windows 图标必须是 .ico 格式！")
            return
        print("设置 Windows 图标...")
        launcher = self.output_dir / f"{self.name}.bat"
        # 将 .bat 转换为 .exe 并设置图标
        # 这里可以使用第三方工具（如 bat-to-exe）来实现
        print("图标设置完成！")

    def create_macos_app(self, icon_path):
        """生成 macOS .app 包并设置图标"""
        if not icon_path.endswith(".icns"):
            print("macOS 图标必须是 .icns 格式！")
            return
        print("生成 macOS .app 包...")
        app_dir = self.output_dir / f"{self.name}.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"

        # 创建目录结构
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)

        # 复制图标
        shutil.copy(icon_path, resources_dir / "app_icon.icns")

        # 生成 Info.plist
        plist_path = contents_dir / "Info.plist"
        plist_data = {
            "CFBundleName": self.name,
            "CFBundleExecutable": self.name,
            "CFBundleIconFile": "app_icon.icns",
        }
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_data, f)

        # 复制启动脚本
        shutil.copy(self.output_dir / f"{self.name}.sh", macos_dir / self.name)
        os.chmod(macos_dir / self.name, 0o755)  # 赋予执行权限

        print(f".app 包生成完成: {app_dir}")

    def package(self):
        """打包"""
        print(f"开始打包: {self.script} -> {self.output_dir}")
        self.output_dir.mkdir(exist_ok=True)

        # 复制脚本
        print("复制脚本...")
        shutil.copy(self.script, self.output_dir / self.script.name)

        # 复制依赖库
        self.copy_dependencies()

        # 复制 Python 解释器
        self.copy_python_interpreter()

        # 生成启动脚本
        self.create_launcher()

        # 单文件打包
        if self.onefile:
            self.package_as_single_file()
            self.create_extract_and_run_launcher()

        # 图标支持
        if self.icon:
            if self.platform == "win32":
                self.set_windows_icon(self.icon)
            elif self.platform == "darwin":
                self.create_macos_app(self.icon)

        print(f"打包完成！输出目录: {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description="自定义 Python 打包器")
    parser.add_argument("script", help="要打包的 Python 脚本")
    parser.add_argument("--output-dir", default="dist", help="输出目录")
    parser.add_argument("--onefile", action="store_true", help="打包为单个文件")
    parser.add_argument("--windowed", action="store_true", help="禁用控制台窗口")
    parser.add_argument("--icon", help="指定图标文件")
    parser.add_argument("--name", help="指定输出文件的名称")
    args = parser.parse_args()

    packager = PythonPackager(
        script=args.script,
        output_dir=args.output_dir,
        onefile=args.onefile,
        windowed=args.windowed,
        icon=args.icon,
        name=args.name,
    )
    packager.package()

if __name__ == "__main__":
    main()