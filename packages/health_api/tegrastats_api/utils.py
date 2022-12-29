import subprocess
import os
import re

from dt_class_utils import DTProcess

GPU_USAGE_RE = re.compile(r"GR3D_FREQ (\d+)%")
GPU_TEMP_RE = re.compile(r"GPU@(\d+(?:\.\d+)?)C")
GPU_POWER_RE = re.compile(r"POM_5V_GPU (\d+)/(\d+)")

gpu_temp = 0.0
gpu_usage = 0
gpu_power_now = 0


def run_tegrastats():
    # Run the tegrastats command
    script_path = os.path.dirname(os.path.abspath(__file__))
    process = subprocess.Popen([script_path + "/tegrastats"], stdout=subprocess.PIPE)
    dtprocess = DTProcess.get_instance()

    # Continuously read and print the output
    while not dtprocess.is_shutdown():
        output = process.stdout.readline().decode("utf-8")
        if output == '' and process.poll() is not None:
            break
        if output:
            try:
                _decode(output)
            except Exception as e:
                print(e)
                pass


def get_gpu_temp():
    return gpu_temp


def get_gpu_usage():
    return gpu_usage


def get_gpu_power():
    return gpu_power_now


def _decode(output):
    global gpu_temp, gpu_usage, gpu_power_now
    gpu_temp_match = GPU_TEMP_RE.search(output)
    gpu_temp = float(gpu_temp_match.group(1))
    gpu_usage_match = GPU_USAGE_RE.search(output)
    gpu_usage = float(gpu_usage_match.group(1))
    gpu_power_match = GPU_POWER_RE.search(output)
    gpu_power_now = int(gpu_power_match.group(1))
    gpu_power_average = int(gpu_power_match.group(1))
