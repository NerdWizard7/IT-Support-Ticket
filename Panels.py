import wx
from Menus import *


class AdminLogin(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.userNameTextCtrl = wx.TextCtrl(self, -1, size=(300, 20))
        self.passwdTxtCtrl = wx.TextCtrl(self, -1, size=(300, 20), style=wx.TE_PASSWORD)

        self.loginButton = wx.Button(self, 20, 'Login')
        self.Bind(wx.EVT_BUTTON, lambda event: parent.login_OnClick(event, self.userNameTextCtrl.GetValue(),
                                                      self.passwdTxtCtrl.GetValue()), self.loginButton)

        sizer.AddStretchSpacer()
        sizer.Add(self.userNameTextCtrl, 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.passwdTxtCtrl, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.loginButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()

        self.SetSizer(sizer)

class ClientLogin(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.userNameTextCtrl = wx.TextCtrl(self, -1, size=(300, 20))
        self.passwdTxtCtrl = wx.TextCtrl(self, -1, size=(300, 20), style=wx.TE_PASSWORD)

        self.loginButton = wx.Button(self, 10, 'Login')
        self.Bind(wx.EVT_BUTTON, lambda event: parent.login_OnClick(event, self.userNameTextCtrl.GetValue(),
                                                      self.passwdTxtCtrl.GetValue()), self.loginButton)

        sizer.AddStretchSpacer()
        sizer.Add(self.userNameTextCtrl, 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.passwdTxtCtrl, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.loginButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

class MainMenu(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        # Box Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label
        font = wx.Font(21, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        mainLabel = wx.StaticText(self, -1, 'IT Support Ticket System')
        mainLabel.SetFont(font)


        # Buttons
        self.adminButton = wx.Button(self, -1, 'Admin', size=(300,30))
        self.Bind(wx.EVT_BUTTON, parent.button_OnClick, self.adminButton)

        self.clientButton = wx.Button(self, -1, 'Client', size=(300,30))
        self.Bind(wx.EVT_BUTTON, parent.button_OnClick, self.clientButton)

        # Add buttons to sizer
        sizer.AddStretchSpacer()
        sizer.Add(mainLabel, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.adminButton, 0, wx.CENTER)
        sizer.Add(self.clientButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()

        # Add sizer to panel
        self.SetSizer(sizer)
