import wx
from Admin import AdminFrame
from Client import ClientFrame


class MainApp(wx.Frame):
    def __init__(self):
        super(MainApp, self).__init__(
            size=(870, 550), parent=None, title='IT Support System')

        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = MainApp()
    app.MainLoop()