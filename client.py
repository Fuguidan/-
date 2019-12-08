# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 19:32:57 2019

@author: FGD
"""
import wx
from time import sleep
import socket
import _thread as thread

class LoginFrame(wx.Frame):
    """
    登录窗口
    """
    def __init__(self, parent, id, title, size):
        # 初始化，添加控件并绑定事件
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.serverAddressLabel = wx.StaticText(self, label="服务端地址", pos=(140, 70), size=(60, 30))
        self.userNameLabel = wx.StaticText(self, label="用户名", pos=(160, 125), size=(40, 30))
        self.serverAddress = wx.TextCtrl(self, pos=(210, 60), size=(170, 30))
        self.userName = wx.TextCtrl(self, pos=(210, 115), size=(170, 30))
        self.loginButton = wx.Button(self, label='登录', pos=(195, 170), size=(130, 30))
        # 绑定登录方法
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
        self.Show()

    def login(self, event):
        # 登录处理
        try:
            serverAddress = self.serverAddress.GetLineText(0).split(':')
            print(serverAddress, self.userName.GetLineText(0))
            sock.connect((serverAddress[0], int(serverAddress[1])))
            sock.send(str(self.userName.GetLineText(0)).encode())
            ChatFrame(None, 2, title='聊天室', size=(622, 418))
            self.Close()
        except Exception:
            self.showDialog('Error', 'Connect Fail!', (200, 100))

    def showDialog(self, title, content, size):
        # 显示错误信息对话框
        dialog = wx.Dialog(self, title=title, size=size)
        dialog.Center()
        wx.StaticText(dialog, label=content)
        dialog.ShowModal()

class ChatFrame(wx.Frame):
    """
    聊天窗口
    """
    def __init__(self, parent, id, title, size):
        # 初始化，添加控件并绑定事件
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(490, 310), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5, 320), size=(490, 50))
        self.small = wx.TextCtrl(self, pos=(500, 185), size=(100, 130), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.sendButton = wx.Button(self, label="发送", pos=(500, 320), size=(100, 50))
        self.usersButton = wx.Button(self, label="用户列表", pos=(500, 5), size=(100, 40))
        self.noticeButton = wx.Button(self, label="公告", pos=(500, 50), size=(100, 40))
        self.secretButton = wx.Button(self, label="私聊", pos=(500, 95), size=(100, 40))
        self.closeButton = wx.Button(self, label="退出", pos=(500, 140), size=(100, 40))
        # 发送按钮绑定发送消息方法
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)
        # Users按钮绑定获取在线用户数量方法
        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)
        # 公告
        self.noticeButton.Bind(wx.EVT_BUTTON, self.notice)
        # 私聊
        self.secretButton.Bind(wx.EVT_BUTTON, self.secret)
        # 关闭按钮绑定关闭方法
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        thread.start_new_thread(self.receive, ())
        self.Show()

    def send(self, event):
        # 发送消息
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            sock.send(message.encode())
            self.message.Clear()

    def lookUsers(self, event):
        # 查看当前在线用户
        sock.send(b'look')

    def notice(self, event):
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            sock.send(('【公告】'+ message).encode())
            self.message.Clear()

    def secret(self, event):
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            sock.send(message.encode())
            self.message.Clear()
    #127.0.0.1:6666
    def close(self, event):
        # 关闭窗口
        sock.send(b'close')
        self.Close()

    def receive(self):
        # 接受服务器的消息
        while True:
            sleep(0.6)
            result = sock.recv(1024).decode()
            check = '【公告】' in result
            if check:
                self.small.AppendText(result)
            elif result != '':
                self.chatFrame.AppendText(result)

if __name__ == '__main__':
    app = wx.App()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    LoginFrame(None, -1, title="let's chat", size=(530, 315))
    app.MainLoop()