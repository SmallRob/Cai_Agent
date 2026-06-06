# 1. 进入正确的子目录
cd E:\WorkSpace\Cai_Agent\cai-agent

# 2. 以开发模式安装
pip install -e .

# 3. 安装完成后，有两种方式启动：
# 方式A：直接用安装后的命令
cai-agent ui -w "E:\WorkSpace\Cai_Agent"

# 方式B：用 python -m（注意是下划线）
python -m cai_agent ui -w "E:\WorkSpace\Cai_Agent"