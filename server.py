# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 19:32:57 2019

@author: FGD
"""

import socket
import threading
# 创建TCP 连接
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定本机的6666端口
sock.bind(('0.0.0.0', 6666))
sock.listen(10)
print('Server', socket.gethostbyname('0.0.0.0'), 'listening ...')

myDict = dict()  # 当前昵称列表
myList = list()  # 当前客户端列表


# 向其他人发送消息
def tellothers(exceptNum, mess):
    for client in myList:
        if client.fileno() != exceptNum:
            try:
                client.send((mess + '\n').encode())
            except Exception as e:
                print('Error: %s' % e)

# 向所有人发送消息
def tellall(exceptNum, mess):
    for client in myList:
        try:
            client.send((mess + '\n').encode())
        except Exception as e:
            print('Error: %s' % e)

# 向自己发送消息
def tellme(exceptNum, mess):
    for client in myList:
        if client.fileno() == exceptNum:
            try:
                client.send((mess + '\n').encode())
            except Exception as e:
                print('Error: %s' % e)

# 向指定的某人发送消息
def tellsomeone(Num, mess):
    for client in myList:
        if client.fileno() == Num:
            try:
                client.send((mess + '\n').encode())
            except Exception as e:
                print('Error: %s' % e)

# 判断名字是否存在 不存在则返回True
def isName(name):
    nameList = list(myDict.values())
    if name not in nameList and name.split():
        return True
    return False

# 根据名字在myDict中查找它的序列值，并返回
def foundcnn(name):
    return list(myDict.keys())[list(myDict.values()).index(name)]

# 发送在线成员
def userlist(myConnection):
    usernum = str(len(myDict))
    # myConnection.send(('在线人数：%s \n' % usernum).encode())
    nameList = list(myDict.values())
    # myConnection.send(('聊天室成员：').encode())
    l = '在线人数：' + usernum + '\n' + '聊天室成员：'
    for name in nameList:
        l = l+name+'、'
    l = l +'\n'
    myConnection.send(l.encode())


def subThreadIn(myConnection, connNumber):
    newuser = ''
    disconnect = False
    # 首先判断该用户名是否存在，
    # 若不存在则break, 且连接成功！
    while True:
        try:
            newuser = myConnection.recv(1024).decode()
        except IOError as e:
            print('Error: %s' % e)
        if isName(newuser):
			# 将新成员名称加入昵称列表
            myDict[connNumber] = newuser  
            # 将新连接加入客户端列表
            myList.append(myConnection)  
            myConnection.send('连接成功！\n'.encode())  
            mContinue = True
            break
        else:
            myConnection.send('连接失败！该用户名已存在！\n'.encode())  # 发送链接失败
            break
    # 连接成功后
    if mContinue:
        # 向其他人发送自己加入房间
        tellothers(connNumber, '【'+ myDict[connNumber] + '】进入聊天室！')
        # 向自己发送登录成功
        tellme(connNumber,'【'+ myDict[connNumber] + '】登录聊天室！')
        # 循环监听消息
        while True:
        	# 当监听到退出指令
            if disconnect:
            	# 告诉自己断开连接
                tellme(connNumber, 'disconnect') 
                # 执行离开操作
                leave(myConnection, connNumber)  
                return
            else:
                try:# 收到消息后的操作
                    order = myConnection.recv(1024)
                    message = order.decode()
                    # message =message.decode()
                    someone1 = str(message).split('：')[0]
                    someone2 = str(message).split(':')[0]
                    # 在服务器段记录所有的聊天记录，并输出
                    print('【', myDict[connNumber], '】：', message)  
                    flag1 = isName(someone1)
                    flag2 = isName(someone2)
                    if not flag1:
                        # 私聊
                        cnn = foundcnn(someone1)
                        tellsomeone(cnn, '【' + myDict[connNumber] + '】（私）：' + str(message).split('：')[1])
                        tellme(connNumber, '【' + myDict[connNumber] + '】（私）：' + str(message).split('：')[1])
                    elif not flag2:
                        cnn = foundcnn(someone2)
                        tellsomeone(cnn, '【' + myDict[connNumber] + '】（私）：' + str(message).split(':')[1])
                        tellme(connNumber, '【' + myDict[connNumber] + '】（私）：' + str(message).split(':')[1])
                    else:
                        # 群聊
                        # 接收到关闭指令
                        if order == b'close' or not message.strip():
                            disconnect = True
                            continue
                        # 接收到查看列表指令
                        elif order == b'look' or not message.strip():
                            userlist(myConnection)
                            continue
                        # 收到公告
                        elif '【公告】' in message:
                            tellall(connNumber, '【' + myDict[connNumber] + '】：'+ '\n' + message)
                        # 受到普通聊天消息
                        else:
                            tellall(connNumber, '【' + myDict[connNumber] + '】：' + message)
                except (OSError, ConnectionResetError):
                	# 异常，则用户断开连接
                    leave(myConnection, connNumber)  
                    return


# 离开函数
def leave(myConnection, connNumber):
    try:# 从客户端列表中删除自己
        myList.remove(myConnection)  
    except ValueError as e: 
        print('Error: %s' % e)
    # 告诉其他人自己离开
    tellothers(connNumber, '【' + myDict[connNumber] + '】离开聊天室！') 
    # 从昵称列表中删除自己
    myDict.pop(connNumber)  
    # 关闭连接
    myConnection.close()  


# 从服务器发布公告，通知所有人
def notice():
    while True:
        noticeM = input()
        for Client in myList:
            try:
                Client.send(('公告：' + noticeM + '\n').encode())
            except Exception as e:
                print('Error: %s' % e)


# 启动一个系统通知线程，以便后续可能发布公告
sendThread = threading.Thread(target=notice)
sendThread.start()

# 循环监听，等待客户端接入
while True:
	# 接入客户端
    connection, address = sock.accept()  
    try:
        # 建立新线程，供所接入的新用户使用
        myThread = threading.Thread(target=subThreadIn, args=(connection, connection.fileno()))
        myThread.setDaemon(True)
        myThread.start()
    except Exception as e:
        print('Error: %s' % e)