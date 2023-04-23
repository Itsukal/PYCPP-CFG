import subprocess
import sys
from djangoPYC_CFG.settings import BASE_DIR
from pathlib import Path
# 设置 Django 项目的根目录和 manage.py 文件路径
print("path:", BASE_DIR);
print(Path(__file__).resolve().parent.parent);
print(sys.path)
project_root = r'/tmp/pycharm_project_138/djangoPYC_CFG'
manage_py_path = fr'{project_root}/manage.py'

# 使用 subprocess 来运行 "python manage.py runserver" 命令
subprocess.call(['python', manage_py_path, 'runserver'])