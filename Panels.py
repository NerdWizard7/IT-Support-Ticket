from Menus import *

class AdminLogin(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        userNameLabel = wx.StaticText(self, -1, 'Username')
        self.userNameTextCtrl = wx.TextCtrl(self, -1, size=(300, 20))
        passwordLabel = wx.StaticText(self, -1, 'Passphrase')
        self.passwdTxtCtrl = wx.TextCtrl(self, -1, size=(300, 20), style=wx.TE_PASSWORD)

        self.loginButton = wx.Button(self, 20, 'Login')
        self.Bind(wx.EVT_BUTTON, lambda event: parent.login_OnClick(event, self.userNameTextCtrl.GetValue(),
                                                      self.passwdTxtCtrl.GetValue()), self.loginButton)

        sizer.AddStretchSpacer()
        sizer.Add(userNameLabel, 0, wx.CENTER)
        sizer.Add(self.userNameTextCtrl, 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(passwordLabel, 0, wx.CENTER)
        sizer.Add(self.passwdTxtCtrl, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.loginButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()

        self.SetSizer(sizer)

class ClientPanel(wx.Panel):
    # Default Constructor
    def __init__(self, parent, username):
        wx.Panel.__init__(self, size=parent.Size, parent=parent)

        #self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))
        # Set up self and status bar
        #self = wx.Panel(self, wx.ID_ANY)

        self.parent = parent

        self.username = username

        # Visual Elements
        box = wx.BoxSizer(wx.VERTICAL)

        # Name Text control (autofilled)
        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topBox.AddSpacer(5)
        nameBox = wx.BoxSizer(wx.VERTICAL)
        nameLabel = wx.StaticText(self, -1)
        nameLabel.SetLabel('Employee Name:')
        self.nameTxtCtrl = wx.TextCtrl(self, -1, size=(130, 20))
        self.nameTxtCtrl.SetValue(self.username)  # Fill value with username from OS
        self.nameTxtCtrl.SetEditable(False)  # Prevent editing
        nameBox.Add(nameLabel)
        nameBox.Add(self.nameTxtCtrl)
        topBox.Add(nameBox)
        topBox.AddSpacer(20)

        # Type choice
        typeBox = wx.BoxSizer(wx.VERTICAL)
        typeList = ['Hardware', 'Software', 'Access', 'Other']
        typeLabel = wx.StaticText(self, -1, pos=(150, 10))
        typeLabel.SetLabel('Request Category:')
        self.typeCombo = wx.ComboBox(self, -1, pos=(150, 30), size=(100, 20))
        for item in typeList:
            self.typeCombo.Append(item)  # Load typeCombo with items in typeList list
        typeBox.Add(typeLabel)
        typeBox.Add(self.typeCombo)
        topBox.Add(typeBox)
        topBox.AddSpacer(20)

        # Priority Choice
        priorityBox = wx.BoxSizer(wx.VERTICAL)
        self.priorityList = ['Low', 'Medium', 'High']
        priorityLabel = wx.StaticText(self, -1, pos=(270, 10))
        priorityLabel.SetLabel('Job Priority:')
        self.priorityChoice = wx.Choice(self, -1, pos=(270, 30), choices=self.priorityList)
        priorityBox.Add(priorityLabel)
        priorityBox.Add(self.priorityChoice)
        topBox.Add(priorityBox)
        topBox.AddSpacer(20)

        # Preceeding Task Box
        predBox = wx.BoxSizer(wx.VERTICAL)
        predLabel = wx.StaticText(self, -1)
        predLabel.SetLabel('Preceeding Task:')
        self.predTextCtrl = wx.TextCtrl(self, -1, size=(90, 20))

        # Uncomment to unhide (not implemented yet)
        self.predTextCtrl.Hide()
        predLabel.Hide()

        predBox.Add(predLabel)
        predBox.Add(self.predTextCtrl)
        topBox.Add(predBox)
        topBox.AddSpacer(40)

        # Hidden Checkbox
        self.hiddenCheckBox = wx.CheckBox(self, 30, 'Hidden', pos=(500, 35))
        self.Bind(wx.EVT_CHECKBOX, self.hidden_OnCheck, self.hiddenCheckBox)
        topBox.Add(self.hiddenCheckBox, 0, wx.EXPAND, 1)
        box.Add(topBox)

        # Description Text Box
        descHBox = wx.BoxSizer(wx.HORIZONTAL)
        descHBox.AddSpacer(5)
        descBox = wx.BoxSizer(wx.VERTICAL)
        descLabel = wx.StaticText(self, -1)
        descLabel.SetLabel('Please include a short description of the problem:')
        self.descTxtCtrl = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        descBox.Add(descLabel)
        descBox.Add(self.descTxtCtrl, 1, wx.EXPAND)
        descBox.AddSpacer(5)
        descHBox.Add(descBox, 1, wx.EXPAND)
        descHBox.AddSpacer(5)
        box.Add(descHBox, 1, wx.EXPAND)

        # List Control
        listBox = wx.BoxSizer(wx.HORIZONTAL)
        listBox.AddSpacer(5)
        self.queueList = wx.ListCtrl(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.queueList.InsertColumn(0, 'ID', width=50)
        self.queueList.InsertColumn(1, 'Name', width=135)
        self.queueList.InsertColumn(2, 'Date', width=85)
        self.queueList.InsertColumn(3, 'Category', width=140)
        self.queueList.InsertColumn(4, 'Priority', width=70)
        self.queueList.InsertColumn(5, 'Job Status', width=75)
        self.queueList.InsertColumn(6, 'Hidden', width=wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.listItem_OnClick, self.queueList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.listCol_OnClick, self.queueList)


        listBox.Add(self.queueList, 1, wx.EXPAND)
        listBox.AddSpacer(5)
        box.Add(listBox, 1, wx.EXPAND)

        # Bottom button(s)
        bottomBox = wx.BoxSizer()
        self.submitButton = wx.Button(self, 10, 'Submit Ticket', size=(130, 30))
        self.Bind(wx.EVT_BUTTON, self.submitButton_OnClick, self.submitButton)
        bottomBox.Add(self.submitButton)
        box.Add(bottomBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        box.AddSpacer(5)

        self.SetSizerAndFit(box)

        # Set Up Printing Data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

        try:
            self.refreshDB()
        except:
            self.displayWarning('Something went wrong while displaying the database. Report this incident to '
                                'an administrator immediately.')

    # Methods
    def GetName(self):
        return "Client"

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
        sql = "SELECT ticketId, User.username, completedBy, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isHidden = 0"
        # Create a QueueViewer object called win, passing it sql code (QueueViewer handles its own SQL queries)
        win = QueueViewer(self, 'Full Job Queue', sql,
                          pos=wx.DefaultPosition, size=(795, 450),
                          style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)  # Show the QueueViewer
        win.SetFocus()

    # Called when View > View Completed Jobs is clicked
    def viewCompleted_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Get schema name from static load method in DBManager
        # Write SQL
        sql = "SELECT ticketId, User.username, completedBy, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isHidden = 0 " \
              "AND isComplete = 1 " \
              f"AND username = '{self.username}'"

        print(sql)  # Print SQL code to console (for debugging)
        # Create a QueueViewer object, and pass it SQL code
        win = QueueViewer(self, 'Completed Jobs', sql,
                          pos=wx.DefaultPosition, size=(795, 450))
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

class AdminPanel(wx.Panel):
    # Default Constructor
    def __init__(self, parent, username):
        wx.Panel.__init__(self, size=parent.Size, parent=parent)

        self.sortFlag = False
        #self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))

        self.username = username

        self.parent = parent

        #self.Bind(wx.EVT_CLOSE, self.OnClose)

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
        self.queueListCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
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
        self.addNoteButton = wx.Button(self, 10, 'Notes...', size=(75, 26))
        self.Bind(wx.EVT_BUTTON, self.addNotes_OnClick, self.addNoteButton)
        updateBox.Add(self.addNoteButton, (3, 1))

        # Priority Choice
        self.changePriorityLabel = wx.StaticText(self, -1)
        self.changePriorityLabel.SetLabel('Priority:')
        updateBox.Add(self.changePriorityLabel, (0, 1))

        self.priorityList = ['Low', 'Medium', 'High']
        self.changePriorityChoice = wx.Choice(self, -1, choices=self.priorityList)
        updateBox.Add(self.changePriorityChoice, (1, 1))

        # Status Choice
        self.changeStatusLabel = wx.StaticText(self, -1)
        self.changeStatusLabel.SetLabel('Job Status:')
        updateBox.Add(self.changeStatusLabel, (0, 2))

        self.statusList = ['Submitted', 'In Progress', 'Completed', 'Halted']
        self.changeStatusChoice = wx.Choice(self, -1, choices=self.statusList)
        updateBox.Add(self.changeStatusChoice, (1, 2))

        # Update Button
        self.updateReqButton = wx.Button(self, 20, 'Update')
        self.Bind(wx.EVT_BUTTON, self.updateReqButton_OnClick, self.updateReqButton)
        updateBox.Add(self.updateReqButton, (3, 2))

        updateBox.AddGrowableCol(0)
        updateBox.AddGrowableCol(1)
        updateBox.AddGrowableCol(2)
        box.Add(updateBox)
        box.AddSpacer(20)

        self.SetSizer(box)
        try:
            self.refreshDB()
        except:
            dlg = wx.MessageBox('Something went wrong while displaying the database. Report this incident to '
                                'an administrator immediately.', 'Waring')

    # Methods
    def GetName(self):
        return "Admin"

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
    def OnClose(self, evt):
        print('OnClose method call')
        self.parent.popWinStack()

    def viewCompleted_OnClick(self, evt):
        db = DBManager
        schema = db.load()[3]  # Get schema name from static load method in DBManager
        # Write SQL
        sql = "SELECT ticketId, User.username, completedBy, submitDate, category, priority, jobStatus, isHidden " \
              f"FROM {schema}.Support_Ticket " \
              "INNER JOIN User ON Support_Ticket.submitterId=User.userId " \
              "WHERE isComplete = 1"
        print(sql)  # Print SQL code to console (for debugging)
        # Create a QueueViewer object, and pass it SQL code
        win = QueueViewer(self, 'Completed Jobs', sql,
                          pos=wx.DefaultPosition, size=(795, 450))
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
        if status != 'Completed':
            set = f"priority = '{priority}', jobStatus = '{status}'"
        else:
            set = f"priority = '{priority}', jobStatus = '{status}', isComplete = 1, completedBy = {Credentials.getUserId(self.username)[0][0]}"
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

class ClientLogin(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        userNameLabel = wx.StaticText(self, -1, 'Username')
        self.userNameTextCtrl = wx.TextCtrl(self, -1, size=(300, 20))
        passwordLabel = wx.StaticText(self, -1, 'Passphrase')
        self.passwdTxtCtrl = wx.TextCtrl(self, -1, size=(300, 20), style=wx.TE_PASSWORD)

        self.loginButton = wx.Button(self, 10, 'Login')
        self.Bind(wx.EVT_BUTTON, lambda event: parent.login_OnClick(event, self.userNameTextCtrl.GetValue(),
                                                      self.passwdTxtCtrl.GetValue()), self.loginButton)

        sizer.AddStretchSpacer()
        sizer.Add(userNameLabel, 0, wx.CENTER)
        sizer.Add(self.userNameTextCtrl, 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(passwordLabel, 0, wx.CENTER)
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

        self.connectToDatabaseButton = wx.Button(self, -1, 'Connect to DB', size=(100, 30))
        self.Bind(wx.EVT_BUTTON, parent.connectToDb_OnClick, self.connectToDatabaseButton)

        # Add buttons to sizer
        sizer.AddStretchSpacer()
        sizer.Add(mainLabel, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.adminButton, 0, wx.CENTER)
        sizer.Add(self.clientButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        sizer.Add(self.connectToDatabaseButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()

        # Add sizer to panel
        self.SetSizer(sizer)