from Menus import *
import Panels


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

        # TODO: Make sure to set these variables once the user logs in
        self.username = ''
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
        elif btn == 'Login':
            if id == 10:
                print('Client')
                win = ClientFrame(self.userId)
                win.Show()
                self.Close()
            elif id == 20:
                print('Admin')
                win = AdminFrame(self.userId)
                win.Show()
                self.Close()

# Main Program Loop
if __name__ == '__main__':
    app = wx.App(False)
    frame = MainApp()
    frame.Show()
    app.MainLoop()