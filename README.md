# BandwagonHost
用于home assistant平台的搬瓦工状态监视器,可以监视搬瓦工VPS的流量、内存、硬盘、负载和IP状态。  

## 安装
请将本项目中custom_components下的bandwagonhost文件夹复制到<config>/custom_components/文件夹下

## 配置 
```yaml
# configuration.yaml

sensor:
  - platform: bandwagonhost
    veid: veid                    # 必须
    api_key: API_KEY              # 必须
    monitored_conditions:         # 可选
      - VPS_STATE                 # 可选，VPS运行状态 Starting, Running or Stopped
      - VPS_LOAD_1M               # 可选，VPS LOAD 1M
      - VPS_LOAD_5M               # 可选，VPS LOAD 5M
      - VPS_LOAD_15M              # 可选，VPS LOAD 15M
      - CURRENT_BANDWIDTH_USED    # 可选，BANDWIDTH 使用量
      - RAM_USED                  # 可选，RAM 使用量
      - DISK_USED                 # 可选，DISK 使用量
      - SWAP_USED                 # 可选，SWAP 使用量
      - VPS_IP                    # 可选，IPv4 and IPv6 addresses assigned to VPS
      - SSH_PORT                  # 可选，SSH port of the VPS
      - HOSTNAME                  # 可选，Hostname of the VPS
      - OS                        # 可选，Operating system
      - NODE_LOCATION             # 可选，Physical location (country, state)
      - DATA_NEXT_RESET           # 可选，Date and time of transfer counter reset (Local Time)
```
以上信息请从搬瓦工的控制页面获取。

## 效果示例
![image](bandwagonhost.png)

## 注意
为了防止因为api请求过于频繁而被搬瓦工封号，传感器每20分钟更新一次。
