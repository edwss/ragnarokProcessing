import signal
import subprocess
import os

class Process:
    def __init__(self):
        self.ports = []
        self.names = []
        self.process = []

    def getPorts(self):
        return self.ports

    def listProcess(self):
        return self.names

    def getpid(self, name):
        return os.getpgid(self.process[self.names.index(name)].pid)

    def add(self, command, name, cwd, virtual_machine = 0, bot_name = 0):
        if virtual_machine:
            self.process.append(subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, preexec_fn=os.setsid,cwd=cwd))
            self.names.append(name)
            dict_ = {}
            dict_['name'] = name
            dict_['vnc_port'] = command.split(' ')[2]
            dict_['qemu_port'] =  command.split(' ')[-1]
            if bot_name:
                dict_['bot_name'] = bot_name
            self.ports.append(dict_)
        else:
            self.process.append(subprocess.Popen('su eduardo', stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, preexec_fn=os.setsid,cwd=cwd))
            self.process[-1].stdin.write('source env/env_python3/bin/activate\n'.encode('utf-8'))
            command_string = '{} &\n'.format(command)
            self.process[-1].stdin.write(command_string.encode('utf-8'))
            self.process[-1].stdin.close()
            self.names.append(name)

    def kill(self, name):
        try:
            os.killpg(os.getpgid(self.process[self.names.index(name)].pid), signal.SIGTERM)
            print(self.process[self.names.index(name)].pid)
            self.process.remove(self.process[self.names.index(name)])
            self.names.remove(name)
        except:
            pass

    def killAll(self):
        for i in range(0, len(self.names)):
            print(self.process[i].pid)
            os.killpg(os.getpgid(self.process[i].pid), signal.SIGTERM)

