import hashlib
import wmi
from getmac import get_mac_address
c = wmi.WMI()

# 获取CPU序列号
def get_cpu_id():
    try:
        cpuId = c.Win32_Processor()[0].ProcessorId
        print("CPU" + cpuId)
        return cpuId
    except Exception as e:
        return "UnknownCPU"

# 获取主板ID（假设系统支持）
def get_motherboard_id():
    try:
        motherboardId = c.Win32_BaseBoard()[0].SerialNumber
        print("Motherboard" + motherboardId)
        return motherboardId
    except Exception as e:
        return "UnknownMotherboard"

# 获取MAC地址
def get_mac_address_info():
    try:
        print("MAC" + get_mac_address())
        return get_mac_address()
    except Exception as e:
        return "UnknownMAC"

# 生成机器码
def get_machine_code():
    # 获取多个硬件信息
    cpu = get_cpu_id()
    motherboard = get_motherboard_id()
    mac = get_mac_address_info()

    # 拼接所有硬件信息
    combined_info = f"{cpu}-{motherboard}-{mac}"
    
    # 对拼接的硬件信息进行哈希加密，生成机器码
    machine_code = hashlib.sha256(combined_info.encode()).hexdigest()
    print("MachineCode" + machine_code)
    return machine_code
