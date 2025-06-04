import os
import requests

"""
脚本: 三福小程序自动签到
作者: 3iXi
创建日期: 2025-06-03
描述: 先开启抓包，再打开“三福会员中心”小程序，抓域名https://crm.sanfu.com URL参数中的sid值（一串英文+数字+符号字符，也可能没有符号）
环境变量：
        变量名：sanfu
        变量格式：sid
        多账号之间用#分隔：sid1#sid2#sid3
"""

def main():
    # 获取环境变量
    env_value = os.getenv('sanfu')
    if not env_value:
        print("未找到环境变量sanfu")
        return
    
    # 分割账号
    accounts = env_value.split('#')
    print(f"本轮共获取到{len(accounts)}个账号信息")
    
    base_url = "https://crm.sanfu.com"
    headers = {
        "Host": "crm.sanfu.com",
        "Connection": "keep-alive",
        "User-Agent": "MicroMessenger/7.0.20.1781",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Referer": "https://servicewechat.com/wxfe13a2a5df88b058/333/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    for i, sid in enumerate(accounts):
        if not sid:
            continue
            
        print(f"\n处理账号 {i+1}/{len(accounts)}")
        
        # 1. 检查账号有效性
        check_url = f"{base_url}/ms-sanfu-wechat-customer/customer/index/equity?sid={sid}"
        try:
            response = requests.get(check_url, headers=headers)
            data = response.json()
            
            if data.get('code') != 200:
                print(f"账号{i+1}检查sid出错，原因: {data.get('msg', '未知错误')}")
                continue
                
            sign_in = data.get('data', {}).get('signIn', 1)
            if sign_in == 1:
                print(f"账号{i+1}今日已签到")
                continue
                
            # 2. 执行签到
            sign_url = f"{base_url}/ms-sanfu-wechat-common/customer/onSign"
            payload = {
                "sid": sid,
                "signWay": 0
            }
            sign_response = requests.post(sign_url, headers=headers, json=payload)
            sign_data = sign_response.json()
            
            if sign_data.get('code') != 200:
                print(f"账号{i+1}签到失败：{sign_data.get('msg', '未知错误')}")
                continue
                
            print(f"完整响应数据: {sign_data}")
            
            # 获取签到返回数据
            onSign_fubi = sign_data.get('data', {}).get('fubi', 0)
            onKeepSignDay = sign_data.get('data', {}).get('onKeepSignDay', 0)
            giftMoneyDaily = sign_data.get('data', {}).get('giftMoneyDaily', 0)
            
            # 3. 获取账号基本信息
            info_url = f"{base_url}/ms-sanfu-wechat-customer/customer/index/baseInfo?sid={sid}"
            info_response = requests.get(info_url, headers=headers)
            info_data = info_response.json()
            
            if info_data.get('code') != 200:
                print(f"账号{i+1}获取基本信息失败：{info_data.get('msg', '未知错误')}")
                continue
                
            curCusId = info_data.get('data', {}).get('curCusId', '未知ID')
            baseInfo_fubi = info_data.get('data', {}).get('fubi', 0)
            
            message = (
                f"{curCusId}签到成功"
                f"连续签到{onKeepSignDay}天"
                f"获得{onSign_fubi}个福币"
                f"再签{giftMoneyDaily}天可得神秘礼物"
                f"当前账号有{baseInfo_fubi}个福币"
            )
            print(message)
            
        except Exception as e:
            print(f"处理账号{i+1}时发生错误: {str(e)}")
            continue

if __name__ == "__main__":
    main()