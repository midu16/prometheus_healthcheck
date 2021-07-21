#############################################################################################
# 2021 - Mihai IDU                                                                          #
#                                                                                           #
# Prometheus highly available switch check                                                  #
#                                                                                           #
#############################################################################################
__author__ = 'Mihai IDU'
__version__ = '0.0.2'

from time import time, sleep
from os import path
import argparse
import os
import socket
import psutil
import time
import subprocess
from subprocess import check_output

"""
CheckHost is sending a ping heartbeat to the specific host you instruct. This will provide a resolution if the remote 
host is reachable.
"""
def CheckHost(hostname):
    try:
        subprocess.check_output(["ping", "-c", "1", hostname])
        return True
    except subprocess.CalledProcessError:
        return False

"""
CheckPort is connecting to the Prometheus port and it validates that the remote and local prometheus instance is working.
"""
def CheckPort(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # 2 Second Timeout
    result = sock.connect_ex((hostname, port))
    if result == 0:
        return True
    else:
        return False
"""
Checking the status of the process.
"""
def CheckProcess(proc_name):
    for proc in psutil.process_iter():
        try:
            if proc_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;
"""
Checking the pid of the process for easy debugg.
"""
def getpid(proc_name):
    return check_output(["pidof",proc_name])

"""
Checking the return code of the prometheus url
"""
def CheckReturnCode():
    return 0
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # defining global variables
    global hostname
    global port
    global proc_name
    global main_host
    global second_host
    text = 'This is prometheus_healthcheck.\nThe following program is design to check the health of' \
           'another prometheus instance in a same environment.'
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("-p", "--port", help="Add a new port of the Prometheus to check", default=9004)
    parser.add_argument("-pn", "--process-name", help="Mention the Prometheus string use to identify the process", default="prometheus")
    parser.add_argument("-v", "--version", action='version',version='%(prog)s ' + __version__)
    parser.add_argument("-mh", "--main-host", type=str, help="Prometheus main host")
    parser.add_argument("-sh", "--second-host", type=str, help="Prometheus second host")
    args = parser.parse_args()
    port = int(args.port)
    proc_name = args.process_name
    hostname = socket.gethostname()
    main_host = args.main_host
    second_host = args.second_host
    while True:
        if CheckProcess(proc_name) == False and CheckHost(hostname) == True:
            print(
                f'\n{time.strftime("%b %d %H:%M:%S")} {hostname} Process [{proc_name}] is NOT running. The host {hostname} is up!')
        elif CheckProcess(proc_name) == True and CheckHost(hostname) == True:
            print(
                f'\n{time.strftime("%b %d %H:%M:%S")} {hostname} Process [{proc_name}] with pid[{int(getpid("prometheus"))}] running')
            print(CheckPort(hostname, port))
        else:
            print(f'\n{time.strftime("%b %d %H:%M:%S")} {hostname} Process is NOT running and host is down!\n'
                  'The Prometheus service on localhost it will be turn on!\n')