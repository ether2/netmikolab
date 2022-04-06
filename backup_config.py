import netmiko
from netmiko import ConnectHandler
import time
import re
import os
from datetime import date

def open_ssh_conn(ip,device_function,username,password,enable,newfile_dir):

    print('[-] [INFO] Capturing on device %s....'%ip)
    try: 
        cisco_rtsw = {
            'device_type': 'cisco_ios',
            'host': ip,
            'username': username,
            'password': password,
            'secret': enable,
        }   
        conn = ConnectHandler(**cisco_rtsw)
        conn.enable()
        hostname = conn.send_command('show run | i hostname').split(' ')[1]

        if device_function == "router":
            selected_cmd_file = open('command_list_router.txt', 'r')
            selected_cmd_file.seek(0)
        elif device_function == "switch":
            selected_cmd_file = open('command_list_switch.txt', 'r')
            selected_cmd_file.seek(0)

        new_f = open(newfile_dir+'\\'+hostname+'.txt','w+')
        for each_line in selected_cmd_file.readlines():
            new_f.write('%s#%s\n'%(hostname,each_line))
            if re.search('% Invalid input detected at', conn.send_command(each_line)):
                print('[-] [INFO] Invalid \"%s\" syntax on device %s' %(each_line.replace('\n',''),hostname))
            else:
                new_f.write(conn.send_command(each_line))

        selected_cmd_file.close()
        new_f.close()
        conn.disconnect()
        print('[-] [INFO] Done for device %s (%s)\n'%(hostname,ip))

    except netmiko.NetmikoAuthenticationException:
        print("[-] [ERROR] Invalid username or password for device %s! Please check the username/password file or the device configuration!\n"%(ip))
    except netmiko.NetmikoTimeoutException:
        print("[-] [ERROR] Connection time out for Device %s\n"%(ip))
    except ValueError:
        print("[-] [ERROR] Failed to enter privilege mode! Please check the \'secret\' password for Device %s\n"%(ip))

if __name__ == '__main__':
    device_list = open('device_list.txt','r')
    ip,device_function,username,password,enable = [],[],[],[],[]
    newfile_dir = "D:\\netmiko\\%s"%date.today().strftime("%d-%m-%Y")
    try:
        print("[-] [INFO] Creating new folder at %s\n"%newfile_dir)
        os.mkdir(newfile_dir)
    except FileExistsError:
        print("[-] [INFO] Folder %s Already Exists!\n"%newfile_dir)

    for x in range(len(device_list.readlines())):
        device_list.seek(0)
        ip.append(device_list.readlines()[x].split(',')[0].rstrip('\n'))
        device_list.seek(0)
        device_function.append(device_list.readlines()[x].split(',')[1].rstrip('\n'))
        device_list.seek(0)
        username.append(device_list.readlines()[x].split(',')[2].rstrip('\n'))
        device_list.seek(0)
        password.append(device_list.readlines()[x].split(',')[3].rstrip('\n'))
        device_list.seek(0)
        enable.append(device_list.readlines()[x].split(',')[4].rstrip('\n'))      
    device_list.close()

    try:
        for x in range(len(ip)):
            open_ssh_conn(ip[x],device_function[x],username[x],password[x],enable[x],newfile_dir)
            if x == len(ip)-1:
                print('[-] [INFO] BACKUP TASK COMPLETE!')
    except KeyboardInterrupt:
        print("[-] [ERROR] Cancel Backup on Keyboard Interrupt!")
