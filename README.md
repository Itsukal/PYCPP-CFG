# PYCPP-CFG

## Installation
请先运行以下命令
apt-get install clang
pip install -r requirements.txt

然后确定你的libclang.so在哪，并将CFG/disposeCFG/clang/main.py里的该代码改成你的libclang.so的我位置
eg：Config.set_library_file('/usr/local/lib/libclang.so');