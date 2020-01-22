import wx
from DB import Query, DBManager
from Menus import DescViewer, NotesEditor, DatabaseMenu, QueueViewer, SQLEdit
from PrintHandler import PrintMe, PrintFormat
import datetime
from pathlib import Path
from Format import ListFormat, Sorter

__author__ = "Caleb A. Smith"
__copyrightLine__ = "Copyright (c) 2019, Caleb A. Smith. All Rights Reserved."
__credits__ = "Caleb A. Smith"
__license__ = "FreeBSD"
__version__ = "0.1.0"
__email__ = "calebsmitty777@gmail.com"
__stage__ = "Alpha"
__status__ = "In Development"

class MyFrame(wx.Frame):
    # Default Constructor
    def __init__(self):
        super(MyFrame, self).__init__(
            size=(870, 520), parent=None, title=f'Support Ticket Administration')

        self.sortFlag = False

        # Set up panel and status bar
        panel = wx.Panel(self, wx.ID_ANY)
        self.CreateStatusBar()
        self.SetStatusText(__copyrightLine__)

        # Menu Setup
        menuBar = wx.MenuBar()

        menu3 = wx.Menu()
        menu3.Append(100, 'Pre&view')
        menu3.Append(110, 'Page &Setup...')
        menu3.Append(120, '&Print...')
        menu3.Append(125, 'Add &Notes...')

        menu4 = wx.Menu()
        menu4.Append(170, "C&ustom SQL")

        menu3.AppendMenu(126, "&Repor&ts", menu4)

        menu3.AppendSeparator()
        menu3.Append(130, '&Refresh')
        menuBar.Append(menu3, '&File')

        menu1 = wx.Menu()
        menu1.Append(160, '&Completed Jobs')
        menuBar.Append(menu1, '&View')

        menu2 = wx.Menu()
        menu2.Append(150, '&Database')
        menuBar.Append(menu2, '&Settings')
        self.SetMenuBar(menuBar)

        # Bind Menu Items to Event Handlers
        self.Bind(wx.EVT_MENU, self.pageSetup_OnClick, id=110)
        self.Bind(wx.EVT_MENU, self.printPreview_OnClick, id=100)
        self.Bind(wx.EVT_MENU, self.print_OnClick, id=120)
        self.Bind(wx.EVT_MENU, self.refresh_OnClick, id=130)
        self.Bind(wx.EVT_MENU, self.addNotes_OnClick, id=125)
        self.Bind(wx.EVT_MENU, self.dataBaseSettings_OnClick, id=150)
        self.Bind(wx.EVT_MENU, self.viewCompleted_OnClick, id=160)
        self.Bind(wx.EVT_MENU, self.customSQL_OnClick, id=170)

        # Set Up Printing Data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

        # Visual Elements

        # List Control
        box = wx.BoxSizer(wx.HORIZONTAL)
        width = wx.LIST_AUTOSIZE
        listBox = wx.BoxSizer(wx.VERTICAL)
        self.queueListCtrl = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.queueListCtrl.InsertColumn(0, 'ID', width=width)
        self.queueListCtrl.InsertColumn(1, 'Name', width=width)
        self.queueListCtrl.InsertColumn(2, 'Date',
                                        width=len(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S') * 8))
        self.queueListCtrl.InsertColumn(3, 'Category', width=width)
        self.queueListCtrl.InsertColumn(4, 'Priority', width=width)
        self.queueListCtrl.InsertColumn(5, 'Job Status', width=width)
        self.queueListCtrl.InsertColumn(6, 'Hidden', width=wx.EXPAND)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.listItem_OnClick, self.queueListCtrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.listItem_OnSelect, self.queueListCtrl)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.listCol_OnClick, self.queueListCtrl)
        listBox.Add(self.queueListCtrl, 1, wx.EXPAND, 20)
        box.Add(listBox, 1, wx.EXPAND, 1)

        updateBox = wx.GridBagSizer()

        # Notes Button
        self.addNoteButton = wx.Button(panel, 10, 'Notes...', size=(75, 26))
        self.Bind(wx.EVT_BUTTON, self.addNotes_OnClick, self.addNoteButton)
        updateBox.Add(self.addNoteButton, (3, 1))

        # Priority Choice
        self.changePriorityLabel = wx.StaticText(panel, -1)
        self.changePriorityLabel.SetLabel('Priority:')
        updateBox.Add(self.changePriorityLabel, (0, 1))

        self.priorityList = ['Low', 'Medium', 'High']
        self.changePriorityChoice = wx.Choice(panel, -1, choices=self.priorityList)
        updateBox.Add(self.changePriorityChoice, (1, 1))

        # Status Choice
        self.changeStatusLabel = wx.StaticText(panel, -1)
        self.changeStatusLabel.SetLabel('Job Status:')
        updateBox.Add(self.changeStatusLabel, (0, 2))

        self.statusList = ['Submitted', 'In Progress', 'Completed', 'Halted']
        self.changeStatusChoice = wx.Choice(panel, -1, choices=self.statusList)
        updateBox.Add(self.changeStatusChoice, (1, 2))

        # Update Button
        self.updateReqButton = wx.Button(panel, 20, 'Update')
        self.Bind(wx.EVT_BUTTON, self.updateReqButton_OnClick, self.updateReqButton)
        updateBox.Add(self.updateReqButton, (3, 2))

        updateBox.AddGrowableCol(0)
        updateBox.AddGrowableCol(1)
        updateBox.AddGrowableCol(2)
        box.Add(updateBox)
        box.AddSpacer(20)

        panel.SetSizerAndFit(box)

        self.Show()
        try:
            self.refreshDB()
        except:
            dlg = wx.MessageBox('Something went wrong while displaying the database. Report this incident to '
                                'an administrator immediately.', 'Waring')
        
    # Methods
    def GetListCtrl(self):
        return self.queueListCtrl

    # This method is called every time the DB needs to be loaded/reloaded
    def refreshDB(self):
        db = DBManager
        schema = db.load()[3]  # Call static load method in DBManager, and get the schema name
        query = Query()
        # Write SQL
        sql = "SELECT ID, Name, Date, Category, Priority, Status, Hidden " \
              f"FROM {schema}.requests " \
              "WHERE Status != 'Completed'"
        result = query.genericQuery(sql, False)  # Make the query and store the result
        ListFormat.listwriter(self, result)

    # Event Handlers

    def customSQL_OnClick(self, evt):
        win = SQLEdit(self, 'SQL Editor',
                      style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)
        win.SetFocus()

    def viewCompleted_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Get schema name from static load method in DBManager
        # Write SQL
        sql = "SELECT ID, Name, Date, Category, Priority, Status, Hidden " \
              f"FROM {schema}.requests " \
              "WHERE Status = 'Completed';"
        print(sql)  # Print SQL code to console (for debugging)
        # Create a QueueViewer object, and pass it SQL code
        win = QueueViewer(self, 'Completed Jobs', sql,
                          pos=wx.DefaultPosition, size=(595, 450))
        win.Show(True)
        win.SetFocus()

    # Called every time a column header is clicked
    def listCol_OnClick(self, evt):
        Sorter.sort(self, evt.GetColumn())

    # dataBaseSettings Handler (Settings > Database)
    def dataBaseSettings_OnClick(self, evt):
        win = DatabaseMenu(self, 'DB Settings',
                           style=wx.DEFAULT_FRAME_STYLE)
        win.SetSize((400, 400))  # Set Menu Size
        win.Show(True)
        win.SetFocus()

    # Called every time you highlight an item in the list
    def listItem_OnSelect(self, evt):
        # Grab info for the row that was clicked
        rowid = self.queueListCtrl.GetFirstSelected()
        priority = self.queueListCtrl.GetItemText(rowid, 4)
        status = self.queueListCtrl.GetItemText(rowid, 5)

        # Set the values of the different boxes you can change
        self.changePriorityChoice.SetStringSelection(priority)
        self.changeStatusChoice.SetStringSelection(status)

    # Called when the Update button is clicked
    def updateReqButton_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Grab the schema name from the DBManager's static load method
        # Get row info
        rowid = self.queueListCtrl.GetFirstSelected()
        id = self.queueListCtrl.GetItemText(rowid, 0)
        priority = self.changePriorityChoice.GetStringSelection()
        status = self.changeStatusChoice.GetStringSelection()

        # Set up values for the update method in Query class
        query = Query()
        dbname = f'{schema}.requests'
        set = f"Priority = '{priority}', Status = '{status}'"
        cond = f"ID = {id}"

        if query.updateTable(dbname, set, cond) == 0:  # Make the query and perform logic on return value
            msg = wx.MessageBox('Support request record was updated successfully.', 'Success')
            self.refreshDB()
        else:
            msg = wx.MessageBox('Something went wrong. Make sure a list item was selected',
                                'Error')

    # Actual event handler for refresh buttons
    def refresh_OnClick(self, evt):
        self.refreshDB()

    # Called every time you actually click on an item in the list
    def listItem_OnClick(self, evt):
        # Grab row information
        rowid = self.queueListCtrl.GetFirstSelected()
        id = self.queueListCtrl.GetItemText(rowid, 0)

        query = Query()
        desc = query.getDescById(id)[0][0]  # Make the query and store the return value in desc (description text)

        # Create a new DescViewer object called win and pass it the returned value from the query
        win = DescViewer(self, 'Request Description', desc=desc, pos=wx.DefaultPosition, size=(430, 430),
                         style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)  # Display the object to the screen
        win.SetFocus()

    # Page Setup Menu Item Event Handler
    def pageSetup_OnClick(self, event):
        PrintMe.pageSetup(self)

    # Print Preview Event Handler
    def printPreview_OnClick(self, event):
        text = PrintFormat.getPrintHeader()  # Set up the text to be rendered in the preview window
        rowcount = self.queueListCtrl.GetItemCount()
        colcount = self.queueListCtrl.GetColumnCount()
        # Add to text depending on row info
        for row in range(rowcount):
            for col in range(colcount):
                if col == colcount - 1:
                    text += self.queueListCtrl.GetItemText(row, col) + '\n'
                else:
                    # Get contents of the queue
                    text += f'{self.queueListCtrl.GetItemText(row, col):{PrintFormat.getSpacing(col)}} '
        PrintMe.printPreview(self, text)  # Call static printPreview function in PrintMe class.

    # Print Event Handler
    def print_OnClick(self, event):
        text = PrintFormat.getPrintHeader()  # Set up the text to be sent to printer
        rowcount = self.queueListCtrl.GetItemCount()
        colcount = self.queueListCtrl.GetColumnCount()
        # Add to text depending on row info
        for row in range(rowcount):
            for col in range(colcount):
                # Get contents of the queue
                if col == colcount - 1:
                    text += self.queueListCtrl.GetItemText(row, col) + '\n'
                else:
                    text += f'{self.queueListCtrl.GetItemText(row, col):{PrintFormat.getSpacing(col)}} '
        PrintMe.print(self, text)  # Call static print function in PrintMe class.

    # Called when you click on Notes Button
    def addNotes_OnClick(self, evt):
        select = self.queueListCtrl.GetFirstSelected()  # Get the row
        # If you acually selected an item...
        if not select == -1:
            id = self.queueListCtrl.GetItemText(select)  # Get item id
            # Create a NotesEditor object called win, and pass it the id
            win = NotesEditor(self, 'Notes Editor', id, pos=wx.DefaultPosition, size=(500, 500),
                             style=wx.DEFAULT_FRAME_STYLE)
            win.Show(True)  # Show the editor
            self.refreshDB()  # Refresh the database after closed

# Main function. Runs the program loop
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
