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
import socket
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

"""
making the remote communication socket for retrieving the status of the prometheus process
"""
def RemoteCheckProcess(second_host, remote_port):
    slave = socket.socket()
    slave.connect((second_host, remote_port))
    # getoutput method executes the command and
    # returns the output.
    output += subprocess.getoutput(command)
    # Encode and send the output of the command to
    # the master machine.
    slave.send(output.encode())
    # close method closes the connection.
    slave.close()

def LocalCheckProcess(proc_name, remote_port):
    # Create socket with socket class.
    master = socket.socket()
    # Host is the IP address of master
    # machine.
    host = "0.0.0.0"
    # This will be the port that the
    # socket is bind.
    # binding the host and port to the
    # socket we created.
    master.bind((host, remote_port))
    # listen method listens on the socket
    # to accept socket connection.
    master.listen(1)
    # This method accept socket connection
    # from the slave machine
    slave, address = master.accept()
    # When the slave is accepted, we can send
    # and receive data in real time
    # input the command from the user
    command = CheckProcess(proc_name)
    # encode the command and send it to the
    # slave machine then slave machine can
    # executes the command
    slave.send(command.encode())
    # If the command is exit, close the connection
    #if command == "exit":
    #    break
    # Receive the output of command, sent by the
    # slave machine.recv method accepts integer as
    # argument and it denotes no.of bytes to be
    # received from the sender.
    output = slave.recv(5000)
    print(output.decode())
    # close method closes the socket connection between
    # master and slave.
    master.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # defining global variables
    global hostname
    global port
    global proc_name
    global main_host
    global second_host
    global remote_port
    text = 'This is prometheus_healthcheck.\nThe following program is design to check the health of' \
           'another prometheus instance in a same environment.'
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("-pp", "--prometheus-port", help="Add a new port of the Prometheus to check", default=9004)
    parser.add_argument("-pn", "--process-name", help="Mention the Prometheus string use to identify the process", default="prometheus")
    parser.add_argument("-v", "--version", action='version',version='%(prog)s ' + __version__)
    parser.add_argument("-mh", "--main-host", type=str, help="Prometheus main host")
    parser.add_argument("-sh", "--second-host", type=str, help="Prometheus second host")
    parser.add_argument("-rp","--remote-port", help="Add a new port of the remote communication between main and second process", default=8989)
    args = parser.parse_args()
    port = int(args.prometheus_port)
    proc_name = args.process_name
    hostname = socket.gethostname()
    main_host = args.main_host
    second_host = args.second_host
    remote_port = args.remote_port
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