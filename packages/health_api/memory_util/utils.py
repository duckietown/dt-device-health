import time

def monitor_mem_usage():
    while True:
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.readlines()

        mem_data = {}
        for line in mem_info:
            if 'MemTotal' in line:
                mem_data['MemTotal'] = int(line.split()[1])
            elif 'MemAvailable' in line:
                mem_data['MemAvailable'] = int(line.split()[1])
            elif 'NvMapMemUsed' in line:
                mem_data['NvMapMemUsed'] = int(line.split()[1])
        print(mem_data)
        time.sleep(1)