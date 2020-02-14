from Menus import *


__author__ = "Caleb A. Smith"
__copyrightLine__ = "Copyright (c) 2019, Caleb A. Smith. All Rights Reserved."
__credits__ = "Caleb A. Smith"
__license__ = "FreeBSD"
__version__ = "0.1.0"
__email__ = "calebsmitty777@gmail.com"
__stage__ = "Alpha"
__status__ = "In Development"


class MainApp(wx.Frame):
    def __init__(self):
        super(MainApp, self).__init__(
            size=(870, 550), parent=None, title='IT Support System')

        # Set up main panel
        panel = wx.Panel(self, wx.ID_ANY)

        # Box Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label
        font = wx.Font(21, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        mainLabel = wx.StaticText(panel, -1, 'IT Support Ticket System')
        mainLabel.SetFont(font)

        versionLabel = wx.StaticText(panel, -1, f'Version {__version__}')


        # Buttons
        self.adminButton = wx.Button(panel, -1, 'Admin', size=(300,30))
        self.Bind(wx.EVT_BUTTON, self.button_OnClick, self.adminButton)

        self.clientButton = wx.Button(panel, -1, 'Client', size=(300,30))
        self.Bind(wx.EVT_BUTTON, self.button_OnClick, self.clientButton)

        # Add buttons to sizer
        sizer.AddStretchSpacer()
        sizer.Add(mainLabel, 0, wx.CENTER)
        sizer.Add(versionLabel, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.adminButton, 0, wx.CENTER)
        sizer.Add(self.clientButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()

        # Add sizer to panel
        panel.SetSizer(sizer)
        self.Show()  # Show the window


    # Button Event Logic
    def button_OnClick(self, evt):
        btn = evt.GetEventObject().GetLabel()  # Get the name of the button and store in btn variable
        if btn == 'Admin':  # Admin Button
            win = AdminFrame()  # Open AdminFrame()
            win.Show()
        elif btn == 'Client':  # Client Button
            win = ClientFrame()  # Open ClientFrame()
            win.Show()


# Main Program Loop
if __name__ == '__main__':
    app = wx.App()
    frame = MainApp()
    app.MainLoop()