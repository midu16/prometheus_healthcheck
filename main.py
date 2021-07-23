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
def CheckPort(remote_host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # 2 Second Timeout
    result = sock.connect_ex((remote_host, port))
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
def RemoteSocket(proc_name, remote_port, remote_host, verbose_level):
    localIP = remote_host
    localPort = remote_port
    bufferSize = 1024
    msgFromServer = str(CheckProcess(proc_name))
    bytesToSend = str.encode(msgFromServer)

    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    # Listen for incoming datagrams
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    while verbose_level == 2:
        clientMsg = "Message from Client:{}".format(message)
        clientIP = "Client IP Address:{}".format(address)
        print(clientMsg)
        print(clientIP)
    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)


def LocalSocket(proc_name, remote_port, remote_host, verbose_level):
    msgFromClient = "Hello UDP Server"
    bytesToSend = str.encode(msgFromClient)
    serverAddressPort = (remote_host, remote_port)
    bufferSize = 1024

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    while verbose_level == 2:
        if str(msgFromServer[0].decode('ascii')) == "False":
            print(
                f'\n{time.strftime("%b %d %H:%M:%S")} Process [{proc_name}] is NOT running')
        else:
            print(
                f'\n{time.strftime("%b %d %H:%M:%S")} Process [{proc_name}] is running')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # defining global variables
    global hostname
    global port
    global proc_name
    global main_host
    global second_host
    global remote_port
    global remote_host
    text = 'This is prometheus_healthcheck.\nThe following program is design to check the health of' \
           'another prometheus instance in a same environment.'
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("-pp", "--prometheus-port", help="Add a new port of the Prometheus to check", default=9004)
    parser.add_argument("-pn", "--process-name", help="Mention the Prometheus string use to identify the process", default="prometheus")
    parser.add_argument("-v", "--version", action='version',version='%(prog)s ' + __version__)
    parser.add_argument("-rh", "--remote-host", type=str, help="Prometheus main host")
    parser.add_argument("-sh", "--second-host", type=str, help="Prometheus second host")
    parser.add_argument("-rp","--remote-port", help="Add a new port of the remote communication between main and second process", default=8989)
    args = parser.parse_args()
    port = int(args.prometheus_port)
    proc_name = args.process_name
    hostname = socket.gethostname()
    remote_host = args.remote_host
    second_host = args.second_host
    remote_port = args.remote_port
    while True:
        if CheckProcess(proc_name) == False and CheckHost(hostname) == True:
            print(
                f'\n{time.strftime("%b %d %H:%M:%S")} {hostname} Process [{proc_name}] is NOT running. The host {hostname} is up!')
        elif CheckProcess(proc_name) == True and CheckHost(hostname) == True:
            print(
                f'\n{time.strftime("%b %d %H:%M:%S")} {hostname} Process [{proc_name}] with pid[{int(getpid(proc_name))}] running')
            print(CheckPort(hostname, port))
        else:
            print(f'\n{time.strftime("%b %d %H:%M:%S")} {hostname} Process is NOT running and host is down!\n'
                  'The Prometheus service on localhost it will be turn on!\n')