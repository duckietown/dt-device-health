import re

REGEXP = re.compile(r'(.+?):\s+(.+?) (.?)B')


#In reference to: https://github.com/rbonghi/jetson_stats/blob/e6e140447640b53ae83797541635a6a58927a68e/jtop/core/memory.py#L29
def poll_meminfo(path="/proc/meminfo"):
    memory_info = {}
    with open(path, "r") as fp:
        for line in fp:
            # Search line
            match = REGEXP.search(line)
            if match:
                key = str(match.group(1).strip())
                value = int(match.group(2).strip())
                unit = str(match.group(3).strip())
                memory_info[key] = {'val': value, 'unit': unit}
    return memory_info
