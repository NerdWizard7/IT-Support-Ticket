import wx
from PrintHandler import PrintMe, PrintFormat
import datetime
from DB import Query, DBManager
import getpass
from Menus import DescViewer, QueueViewer, DatabaseMenu
from pathlib import Path
from Format import ListFormat, Sorter

__author__ = "Caleb A. Smith"
__copyrightLine__ = "Copyright (c) 2019, Caleb A. Smith. All Rights Reserved."
__credits__ = "Caleb A. Smith"
__license__ = "BSD"
__version__ = "0.1.0"
__email__ = "calebsmitty777@gmail.com"
__stage__ = "Alpha"
__status__ = "In Development"

HIDDEN = False

class MyFrame(wx.Frame):
    # Default Constructor
    def __init__(self):
        super(MyFrame, self).__init__(
            parent=None, title=f'Support Ticket Client',
            size=(670, 540), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)

        # Set up panel and status bar
        panel = wx.Panel(self, wx.ID_ANY)
        self.CreateStatusBar()
        self.SetStatusText(__copyrightLine__)

        # Setup menu
        menuBar = wx.MenuBar()

        menu3 = wx.Menu()
        menu3.Append(112, '&Preview')
        menu3.Append(114, '&Page Setup...')
        menu3.Append(115, '&Print...')
        menu3.AppendSeparator()
        menu3.Append(116, '&Refresh')
        menuBar.Append(menu3, '&File')

        menu1 = wx.Menu()
        menu1.Append(105, '&Full Job Queue')
        menu1.Append(106, '&Completed Jobs')
        menuBar.Append(menu1, '&View')

        menu2 = wx.Menu()
        menu2.Append(110, '&Database')
        menuBar.Append(menu2, '&Settings')

        # Bind methods to tie menu items to event handlers
        self.Bind(wx.EVT_MENU, self.dataBaseSettings_OnClick, id=110)
        self.Bind(wx.EVT_MENU, self.refreshButton_OnClick, id=116)
        self.Bind(wx.EVT_MENU, self.viewFullQueue_OnClick, id=105)
        self.Bind(wx.EVT_MENU, self.viewCompleted_OnClick, id=106)
        self.Bind(wx.EVT_MENU, self.print_OnClick, id=115)
        self.Bind(wx.EVT_MENU, self.pageSetup_OnClick, id=114)
        self.Bind(wx.EVT_MENU, self.printPreview_OnClick, id=112)
        self.SetMenuBar(menuBar)

        # Visual Elements
        box = wx.BoxSizer(wx.VERTICAL)

        # Name Text control (autofilled)
        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topBox.AddSpacer(5)
        nameBox = wx.BoxSizer(wx.VERTICAL)
        nameLabel = wx.StaticText(panel, -1)
        nameLabel.SetLabel('Employee Name:')
        self.nameTxtCtrl = wx.TextCtrl(panel, -1, size=(130, 20))
        self.nameTxtCtrl.SetValue(getpass.getuser().upper())  # Fill value with username from OS
        self.nameTxtCtrl.SetEditable(False)  # Prevent editing
        nameBox.Add(nameLabel)
        nameBox.Add(self.nameTxtCtrl)
        topBox.Add(nameBox)
        topBox.AddSpacer(20)

        # Type choice
        typeBox = wx.BoxSizer(wx.VERTICAL)
        typeList = ['Code', 'Adjudication', 'Hardware', 'Software', 'Fee Schedule', 'Access',
                    'Other']
        typeLabel = wx.StaticText(panel, -1, pos=(150, 10))
        typeLabel.SetLabel('Request Category:')
        self.typeCombo = wx.ComboBox(panel, -1, pos=(150, 30), size=(100, 20))
        for item in typeList:
            self.typeCombo.Append(item)  # Load typeCombo with items in typeList list
        typeBox.Add(typeLabel)
        typeBox.Add(self.typeCombo)
        topBox.Add(typeBox)
        topBox.AddSpacer(20)

        # Priority Choice
        priorityBox = wx.BoxSizer(wx.VERTICAL)
        self.priorityList = ['Low', 'Medium', 'High']
        priorityLabel = wx.StaticText(panel, -1, pos=(270, 10))
        priorityLabel.SetLabel('Job Priority:')
        self.priorityChoice = wx.Choice(panel, -1, pos=(270, 30), choices=self.priorityList)
        priorityBox.Add(priorityLabel)
        priorityBox.Add(self.priorityChoice)
        topBox.Add(priorityBox)
        topBox.AddSpacer(20)

        # Preceeding Task Box
        predBox = wx.BoxSizer(wx.VERTICAL)
        predLabel = wx.StaticText(panel, -1)
        predLabel.SetLabel('Preceeding Task:')
        self.predTextCtrl = wx.TextCtrl(panel, -1, size=(90, 20))

        # Uncomment to unhide (not implemented yet)
        self.predTextCtrl.Hide()
        predLabel.Hide()

        predBox.Add(predLabel)
        predBox.Add(self.predTextCtrl)
        topBox.Add(predBox)
        topBox.AddSpacer(40)

        # Hidden Checkbox
        self.hiddenCheckBox = wx.CheckBox(panel, 30, 'Hidden', pos=(500, 35))
        self.Bind(wx.EVT_CHECKBOX, self.hidden_OnCheck, self.hiddenCheckBox)
        topBox.Add(self.hiddenCheckBox, 0, wx.EXPAND, 1)
        box.Add(topBox)

        # Description Text Box
        descHBox = wx.BoxSizer(wx.HORIZONTAL)
        descHBox.AddSpacer(5)
        descBox = wx.BoxSizer(wx.VERTICAL)
        descLabel = wx.StaticText(panel, -1)
        descLabel.SetLabel('Please include a short description of the problem:')
        self.descTxtCtrl = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
        descBox.Add(descLabel)
        descBox.Add(self.descTxtCtrl, 1, wx.EXPAND)
        descBox.AddSpacer(5)
        descHBox.Add(descBox, 1, wx.EXPAND)
        descHBox.AddSpacer(5)
        box.Add(descHBox, 1, wx.EXPAND)

        # List Control
        listBox = wx.BoxSizer(wx.HORIZONTAL)
        listBox.AddSpacer(5)
        self.queueList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.queueList.InsertColumn(0, 'ID', width=50)
        self.queueList.InsertColumn(1, 'Name', width=135)
        self.queueList.InsertColumn(2, 'Date', width=85)
        self.queueList.InsertColumn(3, 'Category', width=140)
        self.queueList.InsertColumn(4, 'Priority', width=70)
        self.queueList.InsertColumn(5, 'Job Status', width=75)
        self.queueList.InsertColumn(6, 'Hidden', width=wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.listItem_OnClick, self.queueList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.listCol_OnClick, self.queueList)

        listBox.Add(self.queueList, 1, wx.GROW)
        listBox.AddSpacer(5)
        box.Add(listBox, 1, wx.GROW)
        box.AddSpacer(10)

        # Bottom button(s)
        bottomBox = wx.BoxSizer()
        self.submitButton = wx.Button(panel, 10, 'Submit Ticket', size=(130,30))
        self.Bind(wx.EVT_BUTTON, self.submitButton_OnClick, self.submitButton)
        bottomBox.Add(self.submitButton)
        box.Add(bottomBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        box.AddSpacer(5)

        panel.SetSizerAndFit(box)

        # Set Up Printing Data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

        self.Show()
        try:
            self.refreshDB()
        except:
            self.displayWarning('Something went wrong while displaying the database. Report this incident to '
                                'an administrator immediately.')

    # Methods
    def GetListCtrl(self):
        return self.queueList

    # Called every time the list needs refreshed
    def refreshDB(self):
        query = Query()
        # Make the query, getting only entries from current user
        historyList = query.selectUser(getpass.getuser().upper())
        ListFormat.listwriter(self, historyList)

    # Display warnings when passed a string value. This method isn't used too much
    def displayWarning(self, warning):
        msg = wx.MessageBox(warning, 'Warning', wx.OK)

    # Validate the form (Make sure all fields are filled)
    def formValidate(self):
        # If logic to make sure all fields are not empty
        if int(len(self.nameTxtCtrl.GetValue())) == 0:
            self.displayWarning('Employee Name field is blank.')
            return 1
        elif int(len(self.typeCombo.GetValue())) == 0:
            self.displayWarning('You still need to enter a request type. You may choose from the dropdown menu,'
                                'or specify your own unique type.')
            return 1
        elif self.priorityChoice.GetSelection() == -1:
            self.displayWarning('You need to specify a ticket priority.')
            return 1
        elif len(self.descTxtCtrl.GetValue()) == 0:
            self.displayWarning('Please provide a description.')
            return 1
        else:
            return 0

    # Event Handlers

    # Called when a column header is clicked
    def listCol_OnClick(self, evt):
        Sorter.sort(self, evt.GetColumn())  # Call the sort method and pass it the column index

    # Page Setup Menu Item Event Handler
    def pageSetup_OnClick(self, evt):
        PrintMe.pageSetup(self)

    # Print Preview Event Handler
    def printPreview_OnClick(self, evt):
        text = PrintFormat.getPrintHeader()  # Set up the text to be rendered in the preview
        rowcount = self.GetListCtrl().GetItemCount()
        colcount = self.GetListCtrl().GetColumnCount()
        # Add the actual content to text
        for row in range(rowcount):
            for col in range(colcount):
                if col == colcount - 1:
                    text += self.GetListCtrl().GetItemText(row, col) + '\n'
                else:
                    # Get contents of the queue
                    text += f'{self.GetListCtrl().GetItemText(row, col):{PrintFormat.getSpacing(col)}} '
        PrintMe.printPreview(self, text)  # Call the printPreview method in PrintMe class (Displays the preview)

    # Print Event Handler
    def print_OnClick(self, evt):
        text = PrintFormat.getPrintHeader()  # Set up the text to be sent to the printer
        rowcount = self.GetListCtrl().GetItemCount()
        colcount = self.GetListCtrl().GetColumnCount()
        # Add the content to text
        for row in range(rowcount):
            for col in range(colcount):
                # Get contents of the queue
                if col == colcount - 1:
                    text += self.GetListCtrl().GetItemText(row, col) + '\n'
                else:
                    text += f'{self.GetListCtrl().GetItemText(row, col):{PrintFormat.getSpacing(col)}} '
        PrintMe.print(self, text)  # Call the print method in the PrintMe class (sends job printer)

    # Called when View > View Full Queue is clicked
    def viewFullQueue_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Grab schema name from static load method in DBManager
        # Write SQL
        sql = "SELECT ID, Name, Date, Category, Priority, Status, Hidden " \
              f"FROM {schema}.requests " \
              "WHERE Hidden = 0"
        # Create a QueueViewer object called win, passing it sql code (QueueViewer handles its own SQL queries)
        win = QueueViewer(self, 'Full Job Queue', sql,
                          pos=wx.DefaultPosition, size=(595, 450),
                          style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)  # Show the QueueViewer
        win.SetFocus()

    # Called when View > View Completed Jobs is clicked
    def viewCompleted_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Get schema name from static load method in DBManager
        # Write SQL
        sql = "SELECT ID, Name, Date, Category, Priority, Status, Hidden " \
              f"FROM {schema}.requests " \
              "WHERE Hidden = 0 " \
              "AND Status = 'Completed' " \
              f"AND Name = '{getpass.getuser().upper()}'"
        print(sql)  # Print SQL code to console (for debugging)
        # Create a QueueViewer object, and pass it SQL code
        win = QueueViewer(self, 'Completed Jobs', sql,
                          pos=wx.DefaultPosition, size=(595, 450))
        win.Show(True)
        win.SetFocus()

    # Called when the hidden checkbox is clicked. This makes sure that it is only set to true when it is clicked
    def hidden_OnCheck(self, evt):
        global HIDDEN
        if self.hiddenCheckBox.IsChecked():
            msg = wx.MessageDialog(self, 'By checking "Hidden", your support request will'
                                         ' not be visible to other employees. Administrators'
                                         ' will still be able to view and process the request', 'Notice',
                                   wx.OK | wx.CANCEL)
            if msg.ShowModal() == wx.ID_OK:
                HIDDEN = not HIDDEN
            else:
                self.hiddenCheckBox.SetValue(False)
            msg.Destroy()
        else:
            HIDDEN = not HIDDEN
        print(HIDDEN)  # Debug

    # Called every time you click on a list item
    def listItem_OnClick(self, evt):
        rowid = self.GetListCtrl().GetFirstSelected()
        id = self.GetListCtrl().GetItemText(rowid, 0)
        print(id)
        query = Query()
        desc = query.getDescById(id)[0][0]  # Make the query, and return a description
        # Create a DescViewer object called win with the returned description
        win = DescViewer(self, 'Description Viewer', desc=desc,
                         pos=wx.DefaultPosition, size=(430, 430),
                         style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)  # Show win
        win.SetFocus()

    # Called when you click the Submit Ticket button
    def submitButton_OnClick(self, evt):
        global HIDDEN
        db = DBManager
        schema = db.load()[3]  # Grab the schema name from the static load method in DBManager
        if self.formValidate() == 0:  # If formValidate returns an exit code of 0 (form checks out)...
            # SQL Query to create a new row with ticket data
            sql = f"INSERT INTO {schema}.requests (Name, Date, Category, Description, Priority, Status, Hidden) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            # Set up values to be added to the database
            val = (f"{self.nameTxtCtrl.GetValue()}",
                   f"{datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
                   f"{self.typeCombo.GetValue()}",
                   f"{self.descTxtCtrl.GetValue()}",
                   f"{str(self.priorityChoice.GetStringSelection())}", "Submitted", HIDDEN)
            query = Query()
            if query.insertData(sql, val, False) == 0:  # Make the Insert Query and make sure it worked (returned 0)
                msg = wx.MessageBox('Submission Completed Successfully!',
                                    'Success!', wx.OK_DEFAULT)
                self.descTxtCtrl.Clear()  # Clear the Description field (what the user just typed)
                self.typeCombo.SetValue('')  # Set type to nothing
                self.hiddenCheckBox.SetValue(False)  # Set hidden checkbox back to false
                if HIDDEN:
                    HIDDEN = not HIDDEN
                self.refreshDB()  # Refresh the List (load the newly inserted ticket)
            else:  # Exit status of query was non-zero (error with connection)
                self.displayWarning('Something went wrong. Make sure the database settings are correct.')

    # Called every time a refresh button is clicked
    def refreshButton_OnClick(self, evt):
        self.refreshDB()

    # Called when Settings > Database is clicked; Opens a DBSettings window
    def dataBaseSettings_OnClick(self, event):
        # Create a DatabaseMenu object called win
        win = DatabaseMenu(self, 'DB Settings',
                           style=wx.DEFAULT_FRAME_STYLE)
        win.SetSize((400, 400))  # Set Menu Size
        win.Show(True)  # Show the menu
        win.SetFocus()

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
