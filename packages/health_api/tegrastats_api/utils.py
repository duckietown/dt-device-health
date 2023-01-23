import os
import re
import subprocess

from dt_class_utils import DTProcess

from health_api.knowledge_base import KnowledgeBase

GPU_USAGE_RE = re.compile(r"GR3D_FREQ (\d+)%")
GPU_TEMP_RE = re.compile(r"GPU@(\d+(?:\.\d+)?)C")
GPU_POWER_RE = re.compile(r"POM_5V_GPU (\d+)/(\d+)")


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


def _decode(output):
    gpu_temp_match = GPU_TEMP_RE.search(output)
    KnowledgeBase.set("GPU_TEMP", float(gpu_temp_match.group(1)))

    gpu_usage_match = GPU_USAGE_RE.search(output)
    KnowledgeBase.set("GPU_USAGE", float(gpu_usage_match.group(1)))

    gpu_power_match = GPU_POWER_RE.search(output)
    KnowledgeBase.set("GPU_POWER", int(gpu_power_match.group(1))/1000.0)
