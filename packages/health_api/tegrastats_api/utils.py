import subprocess
import os
from dt_class_utils import DTProcess

def run_tegrastats():
    # Run the tegrastats command
    script_path = os.path.dirname(os.path.abspath(__file__))
    process = subprocess.Popen([script_path+"/tegrastats"], stdout=subprocess.PIPE)
    dtprocess = DTProcess.get_instance()

    # Continuously read and print the output
    while not dtprocess.is_shutdown():
        output = process.stdout.readline().decode("utf-8")
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())