import os
import subprocess
import yaml
import requests

"""
脚本: 一键运行多个脚本+推送
作者: 3iXi
创建日期: 2024-10-30
需要依赖：pyyaml
描述: 需要配置好cfg.yaml再运行脚本，cfg.yaml可在https://github.com/3ixi/autoscripts下载，需要其他推送平台请自行修改send_wxpusher_message配置
"""

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'cfg.yaml')

with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

# 获取需要运行的脚本列表和wxpusher配置
scripts = config.get('scripts', [])
wxpusher_config = config.get('wxpusher', {})

def execute_script(script_name):
    try:
        # 使用subprocess执行脚本并捕获输出信息
        result = subprocess.run(['python', script_name], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"执行脚本时出错: {e}"

# 推送信息到wxpusher
def send_wxpusher_message(title, message):
    apptoken = wxpusher_config.get('apptoken')
    uids = wxpusher_config.get('uids', [])
    topic_id = wxpusher_config.get('topic_id')
    
    payload = {
        'appToken': apptoken,
        'uids': uids,
        'content': f"{title}\n\n{message}",
        'topicId': topic_id
    }
    
    response = requests.post('https://wxpusher.zjiecode.com/api/send/message', json=payload)
    return response.json()

all_outputs = []

for script in scripts:
    script_name = script['path']
    absolute_script_path = os.path.join(current_dir, script_name)

    print(f"正在执行: {script['name']} ({script_name})")
    output = execute_script(absolute_script_path)

    all_outputs.append(f"{script['name']} 执行结果:\n{output}\n")
    print(output)
    print("\n" + "-" * 50 + "\n")

final_message = "\n".join(all_outputs)
send_wxpusher_message("所有脚本执行结果", final_message)
print("所有脚本执行完毕，已发送结果到 wxpusher。")
