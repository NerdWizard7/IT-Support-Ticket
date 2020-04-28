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
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(900, 600),
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        self.userId = 0

        # Set up main panel
        self.mainMenuPanel = Panels.MainMenu(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.mainMenuPanel, 1, wx.EXPAND)

        self.winStack = []

        self.userId = None

        self.shownPanel = None
        self.shownName = ''

        self.pushWinStack(self.mainMenuPanel)

# ---------------------Menu Bar--------------------------------
    def loadMenuBar(self, shown):
        if shown == "Client":
            clientMenuBar = wx.MenuBar()

            clientMenu3 = wx.Menu()
            clientMenu3.Append(112, '&Preview')
            clientMenu3.Append(114, '&Page Setup...')
            clientMenu3.Append(115, '&Print...')
            clientMenu3.AppendSeparator()
            clientMenu3.Append(116, '&Refresh')
            clientMenu3.Append(117, '&Logout')
            clientMenuBar.Append(clientMenu3, '&File')

            clientMenu1 = wx.Menu()
            clientMenu1.Append(105, '&Full Job Queue')
            clientMenu1.Append(106, '&Completed Jobs')
            clientMenuBar.Append(clientMenu1, '&View')

            self.Bind(wx.EVT_MENU, self.shownPanel.refreshButton_OnClick, id=116)
            self.Bind(wx.EVT_MENU, self.shownPanel.viewFullQueue_OnClick, id=105)
            self.Bind(wx.EVT_MENU, self.shownPanel.viewCompleted_OnClick, id=106)
            self.Bind(wx.EVT_MENU, self.shownPanel.print_OnClick, id=115)
            self.Bind(wx.EVT_MENU, self.shownPanel.pageSetup_OnClick, id=114)
            self.Bind(wx.EVT_MENU, self.shownPanel.printPreview_OnClick, id=112)
            self.Bind(wx.EVT_MENU, self.logout_OnClick, id=117)

            self.SetMenuBar(clientMenuBar)
        elif shown == "Admin":

            adminMenuBar = wx.MenuBar()

            adminMenu3 = wx.Menu()
            adminMenu3.Append(100, 'Pre&view')
            adminMenu3.Append(110, 'Page &Setup...')
            adminMenu3.Append(120, '&Print...')
            adminMenu3.Append(125, 'Add &Notes...')

            adminMenu4 = wx.Menu()
            adminMenu3.Append(126, "&Repor&ts", adminMenu4)
            adminMenu4.Append(127, "Report Generator")

            adminMenu3.AppendSeparator()
            adminMenu3.Append(130, '&Refresh')
            adminMenu3.Append(140, '&Logout')
            adminMenuBar.Append(adminMenu3, '&File')

            adminMenu1 = wx.Menu()
            adminMenu1.Append(160, '&Completed Jobs')
            adminMenuBar.Append(adminMenu1, '&View')

            adminMenu2 = wx.Menu()
            adminMenu2.Append(150, '&Database')
            adminMenu2.Append(180, '&User Administraton')
            adminMenuBar.Append(adminMenu2, '&Settings')
            self.SetMenuBar(adminMenuBar)

            # Bind Menu Items to Event Handlers
            self.Bind(wx.EVT_MENU, self.shownPanel.pageSetup_OnClick, id=110)
            self.Bind(wx.EVT_MENU, self.shownPanel.printPreview_OnClick, id=100)
            self.Bind(wx.EVT_MENU, self.shownPanel.print_OnClick, id=120)
            self.Bind(wx.EVT_MENU, self.shownPanel.refresh_OnClick, id=130)
            self.Bind(wx.EVT_MENU, self.shownPanel.addNotes_OnClick, id=125)
            self.Bind(wx.EVT_MENU, self.shownPanel.dataBaseSettings_OnClick, id=150)
            self.Bind(wx.EVT_MENU, self.shownPanel.viewCompleted_OnClick, id=160)
            self.Bind(wx.EVT_MENU, self.userAdmin_OnClick, id=180)
            self.Bind(wx.EVT_MENU, self.logout_OnClick, id=140)
            self.Bind(wx.EVT_MENU, self.ReportGenerator_OnClick, id=127)
        else:
            pass

    # Button Event Logic
    def button_OnClick(self, evt):
        btn = evt.GetEventObject().GetLabel()  # Get the name of the button and store in btn variable
        id = evt.GetEventObject().GetId()  # Get the id of the button for differentiating between admin and client
        if btn == 'Admin':  # Admin Button
            panel = Panels.AdminLogin(self)
            self.pushWinStack(panel)
            self.Layout()
        elif btn == 'Client':  # Client Button
            panel = Panels.ClientLogin(self)
            self.pushWinStack(panel)
            self.Layout()

    def ReportGenerator_OnClick(self, evt):
        win = ReportGenerator(self, 'Report Generator', style=wx.DEFAULT_FRAME_STYLE)
        win.SetSize((700, 500))
        win.Show(True)
        win.SetFocus()

    def login_OnClick(self, id, u, p):
        if id == 10:
            print('Client')
            valid = Credentials.passwordHasher(u, p)
            if valid == 0 or valid == 1:
                panel = Panels.ClientPanel(self, u)
                self.pushWinStack(panel)
            else:
                msg = wx.MessageBox(valid, 'Login Notice')
        elif id == 20:
            print('Admin')
            valid = Credentials.passwordHasher(u, p)
            if valid == 0:
                panel = Panels.AdminPanel(self, u)
                self.pushWinStack(panel)
            elif valid == 1:
                msg = wx.MessageBox("Looks like you aren't an administrator. Contact IT if this is an error",
                                    'Not Authotized')
            else:
                msg = wx.MessageBox(valid, 'Login Notice')

    def userAdmin_OnClick(self, evt):
        win = UserManagement(self, 'User Administration', style=wx.DEFAULT_FRAME_STYLE)
        win.SetSize((700, 500))
        win.Show(True)
        win.SetFocus()

    def mainMenu_OnClick(self, evt):
        while len(self.winStack) != 1:
            self.popWinStack()

    def connectToDb_OnClick(self, evt):
        # Create a DatabaseMenu object called win
        win = DatabaseMenu(self, 'DB Settings',
                           style=wx.DEFAULT_FRAME_STYLE)
        win.SetSize((400, 400))  # Set Menu Size
        win.Show(True)  # Show the menu
        win.SetFocus()

    def logout_OnClick(self, evt):
        self.popWinStack()

    def refreshWinStack(self):
        print(self.winStack)
        for i in range(len(self.winStack)):
            self.winStack[i].Hide()
        self.winStack[len(self.winStack) - 1].Show()

        self.shownPanel = self.winStack[len(self.winStack) - 1]  # Get the current shown panel object
        self.shownName = self.shownPanel.GetName()
        print(self.shownName)
        self.loadMenuBar(self.shownName)
        self.SetTitle(self.shownPanel.title)

    def pushWinStack(self, newPanel):
        self.winStack.append(newPanel)
        self.refreshWinStack()

    def popWinStack(self):
        self.winStack[len(self.winStack) - 1].Hide()
        self.SetMenuBar(None)
        self.winStack.pop()
        self.refreshWinStack()

# Main Program Loop
if __name__ == '__main__':
    app = wx.App(False)
    frame = MainApp()
    frame.Show()
    frame.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))
    app.MainLoop()
