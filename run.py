import Process
import pika
from pickle import dumps
import time

processController = Process.Process()
processController.add('./machine-disk/virtualmachine.sh Rabbit 2 10 rabbit  4400', 'Rabbit', '.', 'True', '')
processController.add('./machine-disk/virtualmachine.sh Merchant 0 01 merchant  4444', 'Merchant', '.', 'True', 'Robot.Merchant')
processController.add('./machine-disk/virtualmachine.sh VirtualMachine_1 1 02 machine-1  4445', 'VirtualMachine_1', '.', 'True', 'Robot.')
processController.add('./machine-disk/virtualmachine.sh VirtualMachine_2 3 03 machine-2  4446', 'VirtualMachine_2', '.', 'True', 'Robot.1')
time.sleep(60)


credentials = pika.PlainCredentials('eduardo', 'edu12309')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.0.0.112', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='Machines')
channel.basic_publish(exchange='',routing_key='Machines',body=dumps(processController.getPorts()))
connection.close()

processController.add('python Server.py 5556', 'Engine_1', '.')

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
except KeyboardInterrupt:
    processController.killAll()
