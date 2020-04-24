import Process

processController = Process.Process()
processController.add('./virtualmachine.sh 5900 01 machine-1  4444', 'VirtualMachine_1', '.', 'True')
processController.add('python server.py 5556 5900 4444', 'Engine_1', '.')

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