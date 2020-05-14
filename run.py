import Process
import Server
from pickle import dumps
import time
import threading
import subprocess
import WebServer

processController = Process.Process()
processController.add('./machine-disk/virtualmachine.sh Merchant 2 0 01 merchant  4444', 'Merchant', '.', 'True', 'Robot.Merchant')
processController.add('./machine-disk/virtualmachine.sh VirtualMachine_1 3 1 02 machine-1  4445', 'VirtualMachine_1', '.', 'True', 'Robot.')
processController.add('./machine-disk/virtualmachine.sh VirtualMachine_2 3 2 03 machine-2  4446', 'VirtualMachine_2', '.', 'True', 'Robot.1')

Server.Functions.machines = processController.getPorts()
Server.socket_port = 5556
threading.Thread(target=Server.main, args=()).start()
webServer = threading.Thread(target=WebServer.main).start()
WebServer.machines = Server.Functions.machines

try:
    while True:
            command = input().split(' ')

            if command[0] == 'list':
                processes = processController.listProcess()
                for i in range(0,len(processes)):
                    print('{}. {} - {}'.format(i, processes[i], processController.getpid(processes[i])))
                    
            if command[0] == 'kill':
                processes = processController.listProcess()
                print('Process {} killed'.format(processes[int(command[1])]))
                processController.kill(processes[int(command[1])])

            if command[0] == 'add':
                command_name = command[1]
                command_pwd = command[2]
                command_string = " ".join(command[3:])
                processController.add(command_string, command_name, command_pwd)
                print('Process added {} : {}'.format(command_name, command_string))

            if command[0] == 'machines':
                print(Server.Functions.machines)

            if command[0] == 'script':
                Server.Functions.script_file('send_wings', 'Robot.Merchant', request='Robot.')
                Server.Functions.script_file('get_wings', 'Robot.', 'Robot.Merchant')
except KeyboardInterrupt:
    processController.killAll()
    exit(0)
