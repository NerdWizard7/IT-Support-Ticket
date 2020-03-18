from Menus import *
import Panels
from Credentials import Credentials

__author__ = "Caleb A. Smith"
__copyrightLine__ = "Copyright (c) 2020, Caleb A. Smith, et al. All Rights Reserved."
__credits__ = "Caleb Smith, Ryan Hinkley, Kolton Harville, Yaovi Soedjede"
__license__ = "FreeBSD"
__version__ = "0.1.0"
__email__ = "calebsmitty777@gmail.com"
__stage__ = "Alpha"
__status__ = "In Development"


class MainApp(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='IT Support System', size=(800, 500))


        self.userId = 0

        # Set up main panel
        self.mainMenuPanel = Panels.MainMenu(self)
        self.adminPanel = Panels.AdminLogin(self)
        self.adminPanel.Hide()
        self.clientPanel = Panels.ClientLogin(self)
        self.clientPanel.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.mainMenuPanel, 1, wx.EXPAND)
        self.sizer.Add(self.adminPanel, 1, wx.EXPAND)
        self.sizer.Add(self.clientPanel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.winStack = [self]


    # Button Event Logic
    def button_OnClick(self, evt):
        btn = evt.GetEventObject().GetLabel()  # Get the name of the button and store in btn variable
        id = evt.GetEventObject().GetId()  # Get the id of the button for differentiating between admin and client
        if btn == 'Admin':  # Admin Button
            self.mainMenuPanel.Hide()
            self.adminPanel.Show()
            self.SetTitle('Administrator Login')
            self.Layout()
        elif btn == 'Client':  # Client Button
            self.mainMenuPanel.Hide()
            self.clientPanel.Show()
            self.SetTitle('Client Login')
            self.Layout()

    def login_OnClick(self, evt, u, p):
        id = evt.GetEventObject().GetId()
        if id == 10:
            print('Client')
            valid = Credentials.passwordHasher(u, p)
            if valid == 0 or valid == 1:
                self.pushWinStack(ClientFrame(self, u))
            else:
                msg = wx.MessageBox(valid, 'Login Notice')

        elif id == 20:
            print('Admin')
            valid = Credentials.passwordHasher(u, p)
            if valid == 0:
                self.pushWinStack(AdminFrame(self, u))
            elif valid == 1:
                msg = wx.MessageBox("Looks like you aren't an administrator. Contact IT if this is an error",
                                    'Not Authotized')
            else:
                msg = wx.MessageBox(valid, 'Login Notice')

    def connectToDb_OnClick(self, evt):
        # Create a DatabaseMenu object called win
        win = DatabaseMenu(self, 'DB Settings',
                           style=wx.DEFAULT_FRAME_STYLE)
        win.SetSize((400, 400))  # Set Menu Size
        win.Show(True)  # Show the menu
        win.SetFocus()

    def refreshWinStack(self):
        self.winStack[len(self.winStack) - 1].Restore()
        for i in range(len(self.winStack)):
            if i != len(self.winStack) - 1:
                self.winStack[i].Close()

    def pushWinStack(self, newWindow):
        self.winStack.append(newWindow)
        self.refreshWinStack()

    def popWinStack(self):
        self.winStack.pop(len(self.winStack) - 1)
        self.refreshWinStack()



# Main Program Loop
if __name__ == '__main__':
    app = wx.App(False)
    frame = MainApp()
    frame.Show()
    frame.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))
    app.MainLoop()
