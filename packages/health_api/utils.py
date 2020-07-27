import subprocess


def command_output(cmd, key, default='ND'):
    cmd = ' '.join(cmd + ['2>/dev/null', '||', 'echo', 'ND'])
    res = subprocess.check_output(cmd, shell=True)
    lines = res.decode('utf-8').split('\n')
    res = {
        key: default
    }
    for line in lines:
        if not line:
            continue
        for c in ['=', ':']:
            if c in line:
                i = line.index(c)
                j = i if '(' not in line else line.index('(')
                res[line[:j].strip()] = line[i + 1:].strip()
                break
    return res
