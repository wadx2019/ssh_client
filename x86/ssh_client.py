# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 20:39:05 2019
@author: HP
"""

import paramiko as pa
import os
import time
last_timestamp=None
last_finshed=None
dimension=None
speed=None
def bytes_count(finished,summary):
    global last_timestamp,last_finshed,dimension,speed
    timestamp=time.time()
    if timestamp-last_timestamp>0.1:
        speed=(finished-last_finshed)/(timestamp-last_timestamp)
        dimension='B/s'
        if speed>1024:
            speed=round(speed/1024,2)
            dimension='KB/s'
            if speed>1024:
                speed=round(speed/1024,2)
                dimension='MB/s'
        last_finshed=finished
        last_timestamp=timestamp
    if speed:
        print("\rfinished:%.2f%% speed:%.2f%s"%(100*finished/summary,speed,dimension),end='')
    else:
        print("\rfinished:%.2f%% speed:~B/s"%(100*finished/summary),end='')
    
class ssh_client:
    def __init__(self,ip="34.92.245.108",port=22,user="root",passwd="dxdst"):
        try:
            self.ip=ip
            self.port=port
            self.user=user
            self.passwd=passwd
            self.client=pa.SSHClient()
            self.client.set_missing_host_key_policy(pa.AutoAddPolicy()) #目的是接受不在本地Known_host文件下的主机。
            self.client.connect(ip,port,user,passwd)
            self.trans=pa.Transport((self.ip, self.port))
            self.trans.connect(username=self.user,password=self.passwd)
            self.sftp=pa.SFTPClient.from_transport(self.trans)
            self.ssh=self.client.invoke_shell()
            self.__echo=None
            self.__cmd=None
        except Exception as e:
            print("\a",end='')
            print(e)
            self.close()
    def get_msg(self,cmd=''):
        try:
            self.__cmd=cmd
            self.ssh.send(self.__cmd+'\n')
        except Exception as e:
            print('\a',end='')
            print(e)
            self.close()
    def put_msg(self):
        try:
            self.__echo=''
            while True:
                time.sleep(0.1)
                if self.ssh.recv_ready():
                    echo=self.ssh.recv(2048)
                    self.__echo+=echo.decode()
                else:
                    break
        except Exception as e:
            print('\a',end='')
            print(e)
            self.close()
    def upload(self,localpath,remotepath):
        global last_timestamp,last_finshed
        last_timestamp=time.time()
        last_finshed=0
        try:
            self.sftp.put(localpath,remotepath,callback=bytes_count)
        except Exception as e:
            print('\a',end='')
            print(e)
            self.close()
    def download(self,localpath,remotepath):
        global last_timestamp,last_finshed
        last_timestamp=time.time()
        last_finshed=0
        try:
            self.sftp.get(remotepath,localpath,callback=bytes_count)
        except Exception as e:
            print('\a',end='')
            print(e)
            self.close()
    @property
    def echo(self):
        if self.__cmd and self.__echo.startswith(self.__cmd):
                return '\n'.join(self.__echo.split('\n')[1:])
        else:
                return self.__echo

    def close(self):
        self.client.close()
        self.trans.close()
        
ip=input("Please input the ip you want to connect: ")
port=int(input("Please input ssh port: "))
user=input("Please input the user name: ")
passwd=input("Please input the password: ")
if ip:
    ssh=ssh_client(ip,port,user,passwd)
else:
    ssh=ssh_client()
switch=input("Please choose action you want [0:ssh,1:sftp] :")
if switch=='0':
    while 1:
        ssh.put_msg()
        print(ssh.echo,end='')
        cmd=input()
        if cmd=='ssh exit':
            break
        ssh.get_msg(cmd)
else:
    switch=input("Please choose action you want [0:upload,1:download] :")
    localpath=input("Please input localpath:")
    remotepath=input("Please uinput remotepath:")
    if switch=='0':
        ssh.upload(localpath,remotepath)
    else:
        ssh.download(localpath,remotepath)
ssh.close()
