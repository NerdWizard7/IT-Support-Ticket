import wx.lib.editor as editor
import json
import sqlparse
import wx
from DB import Query, DBManager
from PrintHandler import PrintMe, PrintFormat
import datetime
from Format import ListFormat, Sorter
from Credentials import Credentials

HIDDEN = False


class ClientFrame(wx.Frame):
    # Default Constructor
    def __init__(self, username):
        super(ClientFrame, self).__init__(
            parent=None, title=f'Support Ticket Client',
            size=(670, 540), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)

        # Set up panel and status bar
        panel = wx.Panel(self, wx.ID_ANY)

        self.username = username

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
        self.nameTxtCtrl.SetValue(self.username)  # Fill value with username from OS
        self.nameTxtCtrl.SetEditable(False)  # Prevent editing
        nameBox.Add(nameLabel)
        nameBox.Add(self.nameTxtCtrl)
        topBox.Add(nameBox)
        topBox.AddSpacer(20)

        # Type choice
        typeBox = wx.BoxSizer(wx.VERTICAL)
        typeList = ['Hardware', 'Software', 'Access', 'Other']
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
        historyList = query.selectUser(self.username)
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
        sql = "SELECT ticketId, User.username, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isHidden = 0"
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
        sql = "SELECT ticketId, User.username, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isHidden = 0 " \
              "AND isComplete = 1 " \
              f"AND username = '{self.username}'"

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
            query = Query()
            if query.insertTicket(Credentials.getUserId(self.nameTxtCtrl.GetValue())[0][0], self.typeCombo.GetValue(),
                                  HIDDEN, str(self.priorityChoice.GetStringSelection()),
                                  self.descTxtCtrl.GetValue()) == 0:  # Make the Insert Query and make sure it worked
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
'''
if __name__ == '__main__':
    app = wx.App()
    frame = ClientFrame()
    app.MainLoop()
'''


class AdminFrame(wx.Frame):
    # Default Constructor
    def __init__(self, username):
        super(AdminFrame, self).__init__(
            size=(870, 520), parent=None, title=f'Support Ticket Administration')

        self.sortFlag = False

        self.username = username

        # Set up panel and status bar
        panel = wx.Panel(self, wx.ID_ANY)
        self.CreateStatusBar()

        # Menu Setup
        menuBar = wx.MenuBar()

        menu3 = wx.Menu()
        menu3.Append(100, 'Pre&view')
        menu3.Append(110, 'Page &Setup...')
        menu3.Append(120, '&Print...')
        menu3.Append(125, 'Add &Notes...')

        menu4 = wx.Menu()
        menu4.Append(170, "C&ustom SQL")

        menu3.Append(126, "&Repor&ts", menu4)

        menu3.AppendSeparator()
        menu3.Append(130, '&Refresh')
        menuBar.Append(menu3, '&File')

        menu1 = wx.Menu()
        menu1.Append(160, '&Completed Jobs')
        menuBar.Append(menu1, '&View')

        menu2 = wx.Menu()
        menu2.Append(150, '&Database')
        menu2.Append(180, '&User Administraton')
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
        sql = "SELECT ticketId, User.username, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isComplete = 0"
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
        sql = "SELECT ticketId, User.username, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isComplete = 1"
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
        dbname = f'{schema}.Support_Ticket'
        set = f"priority = '{priority}', jobStatus = '{status}'"
        cond = f"ticketId = {id}"

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

'''
# Main function. Runs the program loop
if __name__ == '__main__':
    app = wx.App()
    frame = AdminFrame()
    app.MainLoop()
'''


class DatabaseMenu(wx.MiniFrame):
    # Default Constructor for Database Menu
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)  # Default Constructor
        panel = wx.Panel(self, -1)

        # Visual Elements

        # Host Text Control
        self.hostTxtCtrl = wx.TextCtrl(panel, -1, pos=(10, 25), size=(100, 20))
        hostLabel = wx.StaticText(panel, -1, pos=(10, 5))
        hostLabel.SetLabel('Host Name:')

        # Username Text Control
        self.userTxtCtrl = wx.TextCtrl(panel, -1, pos=(10, 70), size=(100, 20))
        userLabel = wx.StaticText(panel, -1, pos=(10, 50))
        userLabel.SetLabel('Database User:')

        # Password Text Control
        self.passwdTxtCtrl = wx.TextCtrl(panel, -1, pos=(10, 115), size=(100, 20), style=wx.TE_PASSWORD)
        passwdLabel = wx.StaticText(panel, -1, pos=(10, 95))
        passwdLabel.SetLabel('Passphrase:')

        # Database Schema Name Text Control
        self.dbNameTxtCtrl = wx.TextCtrl(panel, -1, pos=(10, 160), size=(100, 20))
        dbNameLabel = wx.StaticText(panel, -1, pos=(10, 140))
        dbNameLabel.SetLabel('Schema Name:')

        # Apply Button
        self.applyButton = wx.Button(panel, 10, 'Apply', pos=(10, 200))
        self.Bind(wx.EVT_BUTTON, self.apply_OnClick, self.applyButton)

        # Load data from config file
        db = DBManager
        data = db.load()

        # Load text controls from config file
        self.hostTxtCtrl.SetValue(data[0])
        self.userTxtCtrl.SetValue(data[1])
        self.passwdTxtCtrl.SetValue(data[2])
        self.dbNameTxtCtrl.SetValue(data[3])

    # Called every time the apply button is clicked
    def apply_OnClick(self, evt):
        db = DBManager  # Create a DBManager object called
        # Save contents of text controls to config file via DBManager's static save method
        db.save(self.hostTxtCtrl.GetValue(), self.userTxtCtrl.GetValue(),
                self.passwdTxtCtrl.GetValue(), self.dbNameTxtCtrl.GetValue())
        self.Close()  # Close the window

class DescViewer(wx.MiniFrame):
    # Default Constructor
    def __init__(self, parent, title, desc, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)

        # Setup print data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

        # Visual Elements
        box = wx.BoxSizer(wx.VERTICAL)

        # Description Text Box
        self.descTxtCtrl = wx.TextCtrl(panel, -1, pos=(10, 10), size=(400, 400),
                                       style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        self.descTxtCtrl.WriteText(desc)  # Write the description to the textbox
        self.descTxtCtrl.SetEditable(False)  # Make un-editable
        box.Add(self.descTxtCtrl, 1, wx.EXPAND, 1)

        # Print Preview Button
        buttonBox = wx.BoxSizer(wx.HORIZONTAL)
        self.printPrevButton = wx.Button(panel, -1, 'Preview...')
        self.Bind(wx.EVT_BUTTON, self.printPreview_OnClick, self.printPrevButton)
        buttonBox.Add(self.printPrevButton)

        # Print Button
        self.printButton = wx.Button(panel, -1, 'Print...')
        self.Bind(wx.EVT_BUTTON, self.print_OnClick, self.printButton)
        buttonBox.Add(self.printButton)
        box.Add(buttonBox, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)

        panel.SetSizerAndFit(box)

    # Print Preview Event Handler (called when button clicked)
    def printPreview_OnClick(self, evt):
        text = self.descTxtCtrl.GetValue()  # Get text from textbox
        PrintMe.printPreview(self, text)  # Send text to be rendered by PrintMe.printPreview

    # Print Event Handler (called when button clicked)
    def print_OnClick(self, evt):
        text = self.descTxtCtrl.GetValue()  # Get text from textbox
        PrintMe.print(self, text)  # Send text to PrintMe.print method (sends to printer)


class NotesEditor(wx.MiniFrame):
    # Default constructor
    def __init__(self, parent, title, id, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)
        self.id = id

        # Visual Elements
        self.ed = editor.Editor(panel, -1, style=wx.SUNKEN_BORDER)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.ed, 1, wx.ALL | wx.GROW, 5)
        panel.SetSizer(box)
        panel.SetAutoLayout(True)

        box2 = wx.BoxSizer(wx.HORIZONTAL)

        # Save button
        self.saveButton = wx.Button(panel, 10, 'Write Notes')
        self.Bind(wx.EVT_BUTTON, self.saveButton_OnClick, self.saveButton)

        # Cancel button
        self.cancelButton = wx.Button(panel, 20, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.cancelButton_OnClick, self.cancelButton)

        # Print Button
        self.printButton = wx.Button(panel, 30, 'Print...')
        self.Bind(wx.EVT_BUTTON, self.print_OnClick, self.printButton)

        box2.Add(self.saveButton, 2, wx.ALL, 1)
        box2.Add(self.cancelButton, 2, wx.ALL, 1)
        box2.Add(self.printButton, 2, wx.ALL, 1)
        box.Add(box2)

        # Set up Printing
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

        # Handle Note Overwriting
        # This block will load notes that have already been writen to a specific entry
        # in the database if they exist. If so, it will set the overwrite flag to 1, allowing
        # the notes to be overwritten to the database.
        self.overwrite = False
        result = self.getNotes(self.id)
        if not result == 1:
            self.overwrite = True
            self.ed.SetText(result)

    # Methods

    # Called to grab notes for a specific request
    def getNotes(self, id):
        db = DBManager
        schema = db.load()[3]
        query = Query()
        sql = f"SELECT text " \
              f"FROM {schema}.Note " \
              f"WHERE ticketId = {id}"
        try:
            result = query.genericQuery(sql, False)
            return json.loads(result[0][0])
        except:
            return 1

    # Event Handlers

    # Print Event Handler
    def print_OnClick(self, event):
        list = self.ed.GetText()  # Grab text from the file display
        text = ''
        for item in list:
            text += item + '\n'
        PrintMe.print(self, text)

    # Save button Event Handler
    def saveButton_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Load schema name from static load method in DBManager class
        text = self.ed.GetText()  # Get text from editor
        query = Query()
        # If logic to determine if this is a new note or not
        if self.overwrite == False:  # If it is a new note...
            # SQL
            sql = f"INSERT INTO {schema}.Note " \
                  f"VALUES (%s, %s)"
            val = (f"{self.id}", f"{json.dumps(text)}")  # Values to be inserted
            if query.insertData(sql, val, False) == 0:  # Make query
                msg = wx.MessageBox('Notes Added Successcully!', 'Success!')
            else:
                msg = wx.MessageBox('Something went wrong. Contact a system administrator immediately.',
                                    'Error')
        else:  # Not a new note
            # Set up conditions for the update method in Query class
            condition = f"ticketId = {self.id}"
            set = f"text = '{json.dumps(text)}'"
            dbname = f'{schema}.Note'
            if query.updateTable(dbname, set, condition) == 0:  # Make the query
                msg = wx.MessageBox('Notes Updated Successcully!', 'Success!')
            else:
                msg = wx.MessageBox('Something went wrong. Contact a system administrator immediately.',
                                    'Error')
        self.Close()

    # Cancel button
    def cancelButton_OnClick(self, evt):
        self.Close()

class QueueViewer(wx.MiniFrame):
    # Default Constructor
    def __init__(self, parent, title, sql, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)

        self.sql = sql

        # Visual Elements
        box = wx.BoxSizer(wx.VERTICAL)

        # List Control
        self.queueListCtrl = wx.ListCtrl(panel, size=(560, 400), style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        self.queueListCtrl.InsertColumn(0, 'ID', width=50)
        self.queueListCtrl.InsertColumn(1, 'Name', width=135)
        self.queueListCtrl.InsertColumn(2, 'Date', width=85)
        self.queueListCtrl.InsertColumn(3, 'Category', width=140)
        self.queueListCtrl.InsertColumn(4, 'Priority', width=70)
        self.queueListCtrl.InsertColumn(5, 'Job Status', width=100)
        self.queueListCtrl.InsertColumn(6, 'Hidden', width=wx.EXPAND)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.listItem_OnClick, self.queueListCtrl)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.listCol_OnClick, self.queueListCtrl)
        box.Add(self.queueListCtrl, 1, wx.EXPAND)

        buttonBox = wx.BoxSizer(wx.HORIZONTAL)

        # Print Preview Button
        self.printPrevButton = wx.Button(panel, -1, 'Preview...')
        buttonBox.Add(self.printPrevButton)
        self.Bind(wx.EVT_BUTTON, self.printPreview_OnClick, self.printPrevButton)

        # Print Button
        self.printButton = wx.Button(panel, -1, 'Print...')
        buttonBox.Add(self.printButton)
        self.Bind(wx.EVT_BUTTON, self.print_OnClick, self.printButton)

        box.Add(buttonBox, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)

        panel.SetSizerAndFit(box)
        self.refreshDB()

        # Set Up Printing Data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

    def GetListCtrl(self):
        return self.queueListCtrl

    # Called when a column header is clicked
    def listCol_OnClick(self, evt):
        Sorter.sort(self, evt.GetColumn())  # Call the sort method and pass it the column index

    # Called when you click a list item
    def listItem_OnClick(self, evt):
        rowid = self.queueListCtrl.GetFirstSelected()
        id = self.queueListCtrl.GetItemText(rowid, 0)  # Get row id
        print(id)
        query = Query()
        desc = query.getDescById(id)[0][0]  # Make query
        # Create DescViewer object called win
        win = DescViewer(self, 'Description Viewer', desc=desc, pos=wx.DefaultPosition, size=(430, 430),
                         style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)  # Display win
        win.SetFocus()

    # Called when list needs reset
    def refreshDB(self):
        query = Query()
        result = query.genericQuery(self.sql, False)  # Make query with SQL code passed to default constructor
        #for item in result:
        #   self.queueListCtrl.Append(item[:])
        ListFormat.listwriter(self, result)

    # Print Preview Event Handler
    def printPreview_OnClick(self, event):
        text = PrintFormat.getPrintHeader()
        # Get row and column count
        rowcount = self.queueListCtrl.GetItemCount()
        colcount = self.queueListCtrl.GetColumnCount()
        # Write rows to the text variable (will be sent to PrintMe)
        for row in range(rowcount):
            for col in range(colcount):
                if col == colcount - 1:
                    text += self.queueListCtrl.GetItemText(row, col) + '\n'
                else:  # Get contents of the queue
                    text += f'{self.queueListCtrl.GetItemText(row, col):{PrintFormat.getSpacing(col)}} '
        PrintMe.printPreview(self, text)  # Send text to be rendered in the preview

    # Print Event Handler
    def print_OnClick(self, event):
        text = PrintFormat.getPrintHeader()
        # Get row and column count
        rowcount = self.queueListCtrl.GetItemCount()
        colcount = self.queueListCtrl.GetColumnCount()
        # Write rows to the text variable (will be sent to PrintMe)
        for row in range(rowcount):
            for col in range(colcount):
                if col == colcount - 1:
                    text += self.queueListCtrl.GetItemText(row, col) + '\n'
                else:  # Get contents of the queue
                    text += f'{self.queueListCtrl.GetItemText(row, col):{PrintFormat.getSpacing(col)}}'
        PrintMe.print(self, text)  # Send text to printer

class SQLEdit(wx.MiniFrame):
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)
        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.editorTextCtrl = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
        sizer.Add(self.editorTextCtrl, 1, wx.EXPAND, 1)

        self.submitButton = wx.Button(panel, 10, 'Submit')
        sizer.Add(self.submitButton, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.Bind(wx.EVT_BUTTON, self.submitButton_OnClick, self.submitButton)

        panel.SetSizerAndFit(sizer)


    def submitButton_OnClick(self, evt):
        sql = self.editorTextCtrl.GetValue()
        if len(sqlparse.split(sql)) > 1:
            multi = True
        else:
            multi = False
        result = Query.genericQuery(sql, multi)

        self.Close()

