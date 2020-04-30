import wx.lib.editor as editor
import json
import wx
from DB import Query, DBManager
from PrintHandler import PrintMe, PrintFormat
import datetime
from Format import ListFormat, Sorter
from Credentials import Credentials
import os, sys
import traceback

HIDDEN = False

# Method is used to reference assets that are bundled in with the executable file (such as icons)
# Add any such assets to program.spec file, and run pyinstaller --specpath program.spec to compile
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ReportGenerator(wx.MiniFrame):
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)
        self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))

        self.count = 0

        # Set Up Printing Data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))

        sizer = wx.BoxSizer(wx.VERTICAL)

        label0 = wx.StaticText(panel, -1, 'Date Range')
        sizer.AddSpacer(10)
        sizer.Add(label0, 1, wx.CENTER)

        hsizer0 = wx.BoxSizer(wx.HORIZONTAL)
        hsizervsizer0 = wx.BoxSizer(wx.VERTICAL)
        label0 = wx.StaticText(panel, -1, 'Start')
        self.textBox0 = wx.TextCtrl(panel, -1)
        hsizervsizer0.Add(label0)
        hsizervsizer0.Add(self.textBox0)
        hsizer0.Add(hsizervsizer0)
        hsizer0.AddSpacer(20)

        hsizervsizer1 = wx.BoxSizer(wx.VERTICAL)
        label1 = wx.StaticText(panel, -1, 'End')
        self.textBox1 = wx.TextCtrl(panel, -1)
        hsizervsizer1.Add(label1)
        hsizervsizer1.Add(self.textBox1)
        hsizer0.Add(hsizervsizer1)
        sizer.Add(hsizer0, 1, wx.CENTER)
        sizer.AddSpacer(30)

        self.button = wx.Button(panel, -1, 'Generate Report')
        self.Bind(wx.EVT_BUTTON, self.pressMe_OnClick, self.button)

        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.RadioButton0 = wx.RadioButton(panel, -1, 'Numerical Report')
        hsizer1.Add(self.RadioButton0)
        self.RadioButton0.SetValue(True)
        hsizer1.AddSpacer(20)

        self.RadioButton1 = wx.RadioButton(panel, -1, 'Full Report')
        hsizer1.Add(self.RadioButton1)
        sizer.Add(hsizer1, 1, wx.CENTER)

        vsizer0 = wx.BoxSizer(wx.VERTICAL)
        self.CheckBox0 = wx.CheckBox(panel, -1, 'Completed Tickets')
        vsizer0.Add(self.CheckBox0)
        vsizer0.AddSpacer(15)

        self.CheckBox1 = wx.CheckBox(panel, -1, 'Incomplete Tickets')
        vsizer0.Add(self.CheckBox1)
        vsizer0.AddSpacer(15)

        self.CheckBox2 = wx.CheckBox(panel, -1, 'Graph')
        vsizer0.Add(self.CheckBox2)
        sizer.Add(vsizer0, 1, wx.CENTER)

        sizer.AddStretchSpacer()

        self.gauge = wx.Gauge(panel, -1)
        sizer.Add(self.gauge, 0, wx.CENTER)
        sizer.AddSpacer(5)

        sizer.AddStretchSpacer()
        sizer.Add(self.button, 0, wx.CENTER)
        sizer.AddSpacer(5)

        panel.SetSizerAndFit(sizer)

    def pressMe_OnClick(self, evt):
        try:
            startdate = datetime.datetime.strptime(self.textBox0.GetValue(), '%Y-%m-%d')
            enddate = datetime.datetime.strptime(self.textBox1.GetValue(), '%Y-%m-%d')
            self.count = 0
            self.generateLayout(startdate, enddate)
        except Exception as err:
            msg = wx.MessageBox('Please enter in YYYY-MM-DD format.', 'Invalid Date Format')
            traceback.print_exc()

    def updateProgress(self, size):
        self.count += 1
        if self.count >= size:
            self.count = 0
        self.gauge.SetValue(self.count)

    def generateLayout(self, start, end):
        printHead = f"For date range {start} - {end}:\n\n"
        totalJobs = 0
        completed = 0
        submitted = 0
        halted = 0
        inProgress = 0
        query = Query()
        sql = f"SELECT * FROM Support_Ticket WHERE submitDate BETWEEN '{start}' AND '{end}'"
        result = query.genericQuery(sql, False)
        resultSize = len(result)
        self.gauge.SetRange(resultSize)
        if result != 1:
            for item in result:
                totalJobs += 1
                if item[:][4] == 'Completed':
                    completed += 1
                elif item[:][4] == 'In Progress':
                    inProgress += 1
                elif item[:][4] == 'Halted':
                    halted += 1
                else:
                    submitted += 1
            printHead += f"Total Submitted Jobs: {totalJobs}\n\n" \
                         f"Job Status\n" \
                         f"----------------------------------------\n" \
                         f"Submitted: {submitted}\n" \
                         f"In Progress: {inProgress}\n" \
                         f"Halted: {halted}\n" \
                         f"Completed: {completed}\n\n"
            if self.RadioButton0.GetValue() == True:  # Numerical Report
                PrintMe.printPreview(self, printHead)

            elif self.RadioButton1.GetValue() == True:
                if self.CheckBox0.IsChecked():
                    printHead += f"\nCompleted Tickets: {completed}\n" \
                                 "ID    NAME         DATE/TIME           CATEGORY        COMPLETED BY\n" \
                                 "----- ------------ ------------------- --------------- ----------------\n"
                    for item in result:
                        if item[:][4] == 'Completed':
                            printHead += f"{str(item[:][0]):5} {Credentials.getUsername(item[:][1]):12} " \
                                         f"{str(item[:][2]):19} {item[:][3]:15} " \
                                         f"{Credentials.getUsername(item[:][6]):16}\n"
                        self.updateProgress(resultSize)

                if self.CheckBox1.IsChecked():
                    printHead += f"\nIncomplete Tickets: {submitted + halted + inProgress}\n" \
                                 "ID    NAME         DATE/TIME           CATEGORY\n" \
                                 "----- ------------ ------------------- ---------------\n"
                    for item in result:
                        if item[:][4] != 'Completed':
                            printHead += f"{str(item[:][0]):5} {Credentials.getUsername(item[:][1]):12} " \
                                         f"{str(item[:][2]):19} {item[:][3]:15}\n"
                        self.updateProgress(resultSize)

                if self.CheckBox2.IsChecked():
                    graphBarChar = u'\u2587'
                    maxValue = max([submitted, inProgress, halted, completed])
                    scaleFactor = 30 / maxValue
                    printHead += f"\nGraphs\n" \
                         f"-------------\n" \
                         f"Submitted:  |{graphBarChar * int(submitted * scaleFactor)}\n\n" \
                         f"In Progress:|{graphBarChar * int(inProgress * scaleFactor)}\n\n" \
                         f"Halted:     |{graphBarChar * int(halted * scaleFactor)}\n\n" \
                         f"Completed:  |{graphBarChar * int(completed * scaleFactor)}\n" \
                         f"-------------"

                print(printHead)
                win = DescViewer(self, f"Generated Report", printHead, size=self.Size)
                win.Show()
                win.SetFocus()
        else:
            msg = wx.MessageBox('There was an error generating the report. Try altering the date range and try again.',
                                'Report Error')

class UserManagement(wx.MiniFrame):
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)
        self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)

        listsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.userList = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        width = wx.LIST_AUTOSIZE
        self.userList.InsertColumn(0, 'User ID', width=width)
        self.userList.InsertColumn(1, 'Username', width=width)
        self.userList.InsertColumn(2, 'First Name', width=width)
        self.userList.InsertColumn(3, 'Last Name', width=width)
        self.userList.InsertColumn(4, 'Department', width=width)
        self.userList.InsertColumn(5, 'Role', width=width)
        self.userList.InsertColumn(6, 'Access Level', width=wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.listItem_OnClick, self.userList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.listCol_OnClick, self.userList)

        listsizer.AddSpacer(5)
        listsizer.Add(self.userList, 1, wx.EXPAND)
        listsizer.AddSpacer(5)
        sizer.Add(listsizer, 1, wx.EXPAND)
        sizer.AddSpacer(10)

#-----------------First Horizontal Sizer with Username and Password--------------------------

        textsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        textsizer1v1 = wx.BoxSizer(wx.VERTICAL)
        usernameLabel = wx.StaticText(panel, -1, 'Username: ')
        self.usernameTxtCtrl = wx.TextCtrl(panel, -1)
        self.usernameTxtCtrl.SetMaxLength(12)
        textsizer1v1.Add(usernameLabel)
        textsizer1v1.Add(self.usernameTxtCtrl)
        textsizer1.Add(textsizer1v1)
        textsizer1.AddSpacer(10)

        textsizer1v2 = wx.BoxSizer(wx.VERTICAL)
        passwdLabel = wx.StaticText(panel, -1, 'Password: ')
        self.passwdTxtCtrl = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD)
        textsizer1v2.Add(passwdLabel)
        textsizer1v2.Add(self.passwdTxtCtrl)
        textsizer1.Add(textsizer1v2)

        sizer.Add(textsizer1, 1, wx.CENTER)
        sizer.AddSpacer(10)

#------------------Second Sizer with First and Last Name-------------------------------------

        textsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        textsizer2v1 = wx.BoxSizer(wx.VERTICAL)
        firstNameLabel = wx.StaticText(panel, -1, 'First Name:')
        self.firstNameTxtCtrl = wx.TextCtrl(panel, -1)
        textsizer2.AddSpacer(5)
        textsizer2v1.Add(firstNameLabel)
        textsizer2v1.Add(self.firstNameTxtCtrl)
        textsizer2.Add(textsizer2v1)
        textsizer2.AddSpacer(10)

        textsizer2v2 = wx.BoxSizer(wx.VERTICAL)
        lastNameLabel = wx.StaticText(panel, -1, 'Last Name:')
        self.lastNameTxtCtrl = wx.TextCtrl(panel, -1)
        textsizer2v2.Add(lastNameLabel)
        textsizer2v2.Add(self.lastNameTxtCtrl)
        textsizer2.Add(textsizer2v2)
        textsizer2.AddSpacer(10)

        sizer.Add(textsizer2, 1, wx.CENTER)
        sizer.AddSpacer(10)

#----------------Third Sizer with Department and Access Level---------------------------------------

        textsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        textsizer3v1 = wx.BoxSizer(wx.VERTICAL)
        departmentLabel = wx.StaticText(panel, -1, 'Department:')
        self.departmentTxtCtrl = wx.TextCtrl(panel, -1)
        textsizer3.AddSpacer(5)
        textsizer3v1.Add(departmentLabel)
        textsizer3v1.Add(self.departmentTxtCtrl)
        textsizer3.Add(textsizer3v1)
        textsizer3.AddSpacer(10)

        textsizer3v2 = wx.BoxSizer(wx.VERTICAL)
        accessLevelLabel = wx.StaticText(panel, -1, 'Access Level:')
        accessLevels = ['Standard User', 'Technician', 'Administrator']
        self.accessLevelChoice = wx.Choice(panel, -1, choices=accessLevels)
        textsizer3v2.Add(accessLevelLabel)
        textsizer3v2.Add(self.accessLevelChoice)
        textsizer3.Add(textsizer3v2)
        textsizer3.AddSpacer(10)

        sizer.Add(textsizer3, 1, wx.CENTER)
        sizer.AddSpacer(20)

#----------------------Buttons------------------------------------------------------------

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.updateUserButton = wx.Button(panel, -1, 'Update User')
        buttonsizer.Add(self.updateUserButton)
        buttonsizer.AddSpacer(10)
        self.Bind(wx.EVT_BUTTON, self.updateButton_OnClick, self.updateUserButton)

        self.addUserButton = wx.Button(panel, -1, 'Add User', size=wx.DefaultSize)
        buttonsizer.Add(self.addUserButton)
        buttonsizer.AddSpacer(10)
        self.Bind(wx.EVT_BUTTON, self.addUser_OnClick, self.addUserButton)

        self.removeUserButton = wx.Button(panel, -1, 'Disable User', size=wx.DefaultSize)
        buttonsizer.Add(self.removeUserButton)
        self.Bind(wx.EVT_BUTTON, self.removeUser_OnClick, self.removeUserButton)

        sizer.Add(buttonsizer, 1, wx.CENTER)


        panel.SetSizerAndFit(sizer)

        self.refreshDB()

    def GetListCtrl(self):
        return self.userList

    def refreshDB(self):
        self.userList.DeleteAllItems()
        sql = f"SELECT userId, username, firstName, lastName, department, isAdmin, accessLevel FROM User"
        query = Query()
        users = query.genericQuery(sql, False)
        for user in users:
            if user[:][5] == b'\x01':
                tup = user[:5] + ('Administrator',) + user[6:]
            else:
                tup = user[:5] + ('Standard User',) + user[6:]
            self.userList.Append(tup)

    @staticmethod
    def GetAccessChoice(choicestring):
        if choicestring == 'Standard User':
            return 1
        elif choicestring == 'Technician':
            return 2
        else:
            return 3

    @staticmethod
    def GetAccessChoiceString(choiceint):
        if choiceint == 1:
            return 'Standard User'
        elif choiceint == 2:
            return 'Technician'
        else:
            return 'Administrator'

    def updateButton_OnClick(self, evt):
        if self.GetListCtrl().GetFirstSelected() == -1:
            pass
        else:
            query = Query()
            rowid = self.GetListCtrl().GetFirstSelected()
            userId = self.GetListCtrl().GetItemText(rowid, 0)
            accessLevel = int(self.GetListCtrl().GetItemText(rowid, 6))

            if self.passwdTxtCtrl.GetValue() != '':  # User changed a password (field is not blank)
                sql = f"UPDATE User SET username = '{self.usernameTxtCtrl.GetValue()}', " \
                      f"firstName = '{self.firstNameTxtCtrl.GetValue()}', "\
                      f"lastName = '{self.lastNameTxtCtrl.GetValue()}', " \
                      f"passwordHash = '{Credentials.passwordHash(self.passwdTxtCtrl.GetValue())}', " \
                      f"department = '{self.departmentTxtCtrl.GetValue()}', isAdmin = {1 if self.GetAccessChoice(self.accessLevelChoice.GetStringSelection()) != 0 else 0}, " \
                      f"accessLevel = {self.GetAccessChoice(self.accessLevelChoice.GetStringSelection())} WHERE userId = {userId}"
            else:  # User didn't enter any password; Don't change it.
                sql = f"UPDATE User SET username = '{self.usernameTxtCtrl.GetValue()}', " \
                      f"firstName = '{self.firstNameTxtCtrl.GetValue()}', " \
                      f"lastName = '{self.lastNameTxtCtrl.GetValue()}', " \
                      f"department = '{self.departmentTxtCtrl.GetValue()}', isAdmin = {1 if self.GetAccessChoice(self.accessLevelChoice.GetStringSelection()) != 0 else 0}, " \
                      f"accessLevel = {self.GetAccessChoice(self.accessLevelChoice.GetStringSelection())} WHERE userId = {userId}"
            if query.genericQuery(sql, False) == 1:
                msg = wx.MessageBox('There was an issue with your query. Make sure all boxes are filled.',
                                    'User Update Error')
            else:
                msg = wx.MessageBox('User Successfully Updated!', 'User Update Success')
                self.refreshDB()

    def addUser_OnClick(self, evt):
        query = Query()

        sql = f"INSERT INTO User VALUES (NULL, '{self.usernameTxtCtrl.GetValue()}', " \
              f"'{self.firstNameTxtCtrl.GetValue()}', '{self.lastNameTxtCtrl.GetValue()}', " \
              f"'{Credentials.passwordHash(self.passwdTxtCtrl.GetValue())}', " \
              f"'{self.departmentTxtCtrl.GetValue()}', " \
              f"{1 if self.GetAccessChoice(self.accessLevelChoice.GetStringSelection()) != 0 else 0}, " \
              f"{self.GetAccessChoice(self.accessLevelChoice.GetStringSelection())});"
        if query.genericQuery(sql, False) == 1:
            msg = wx.MessageBox('There was an issue with your query. Make sure all boxes are filled.',
                                    'Add User Error')
        else:
            msg = wx.MessageBox('User Successfully Added!', 'Add User Success')
            self.refreshDB()

    def removeUser_OnClick(self, evt):
        if self.GetListCtrl().GetFirstSelected() == -1:
            pass
        else:
            query = Query()
            rowid = self.GetListCtrl().GetFirstSelected()
            userId = self.GetListCtrl().GetItemText(rowid, 0)

            sql = f'UPDATE User SET accessLevel = 0 WHERE userId = {userId}'
            if query.genericQuery(sql, False) == 1:
                msg = wx.MessageBox('There was an issue with your query. Make sure all boxes are filled.',
                                    'Disable User Error')
            else:
                msg = wx.MessageBox('User Successfully Disabled!', 'Disable User Success')
                self.refreshDB()

    def listCol_OnClick(self, evt):
        Sorter.sort(self, evt.GetColumn())

    def listItem_OnClick(self, evt):
        rowid = self.GetListCtrl().GetFirstSelected()
        id = self.GetListCtrl().GetItemText(rowid, 0)

        self.usernameTxtCtrl.SetValue(self.userList.GetItemText(rowid, 1))
        self.firstNameTxtCtrl.SetValue(self.userList.GetItemText(rowid, 2))
        self.lastNameTxtCtrl.SetValue(self.userList.GetItemText(rowid, 3))
        self.departmentTxtCtrl.SetValue(self.userList.GetItemText(rowid, 4))
        self.accessLevelChoice.SetStringSelection(self.GetAccessChoiceString(int(self.userList.GetItemText(rowid, 6))))
        self.passwdTxtCtrl.SetValue('')

class DatabaseMenu(wx.MiniFrame):
    # Default Constructor for Database Menu
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)  # Default Constructor
        panel = wx.Panel(self, -1)

        self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))

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
        self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))
        # Setup print data
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15, 15), wx.Point(15, 15))
        font = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL)

        # Visual Elements
        box = wx.BoxSizer(wx.VERTICAL)

        # Description Text Box
        self.descTxtCtrl = wx.TextCtrl(panel, -1, pos=(10, 10), size=(400, 400),
                                       style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        self.descTxtCtrl.WriteText(desc)  # Write the description to the textbox
        self.descTxtCtrl.SetEditable(False)  # Make un-editable
        self.descTxtCtrl.SetFont(font)
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
        self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))
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
                  f"VALUES ({self.id}, '{json.dumps(text)}')"
            if query.genericQuery(sql, False) != 1:  # Make query
                msg = wx.MessageBox('Notes Added Successcully!', 'Success!')
            else:
                msg = wx.MessageBox('Something went wrong. Contact a system administrator immediately.',
                                    'Error')
        else:  # Not a new note
            sql = f"UPDATE Note SET text = '{json.dumps(text)}' WHERE ticketId = {self.id}"
            if query.genericQuery(sql, False) != 1:  # Make the query
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
        self.SetIcon(wx.Icon(resource_path('StickyHamsters32x32.ico')))
        # Visual Elements
        box = wx.BoxSizer(wx.VERTICAL)

        # List Control
        self.queueListCtrl = wx.ListCtrl(panel, size=(560, 400), style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        self.queueListCtrl.InsertColumn(0, 'ID', width=50)
        self.queueListCtrl.InsertColumn(1, 'Name', width=135)
        self.queueListCtrl.InsertColumn(2, 'Completed By', width=130)
        self.queueListCtrl.InsertColumn(3, 'Date', width=85)
        self.queueListCtrl.InsertColumn(4, 'Category', width=140)
        self.queueListCtrl.InsertColumn(5, 'Priority', width=70)
        self.queueListCtrl.InsertColumn(6, 'Job Status', width=100)
        self.queueListCtrl.InsertColumn(7, 'Hidden', width=wx.EXPAND)
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
        self.pdata.SetOrientation(wx.LANDSCAPE)
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

    @staticmethod
    def getSpacing(col):  # Special version of this method from PrintHandler. This deals with the extra column.
        if col == 0:
            return '5'
        elif col == 1:
            return '12'
        elif col == 2:
            return '12'
        elif col == 3:
            return '19'
        elif col == 4:
            return '15'
        elif col == 5:
            return '10'
        elif col == 6:
            return '11'
        else:
            return '4'

    # Print Preview Event Handler
    def printPreview_OnClick(self, event):
        text = 'ID    NAME         COMPLETED BY DATE/TIME           CATEGORY        PRIORTY    STATUS      HIDE\n' \
               '----- ------------ ------------ ------------------- --------------- ---------- ----------- ----\n'
        # Get row and column count
        rowcount = self.queueListCtrl.GetItemCount()
        colcount = self.queueListCtrl.GetColumnCount()
        # Write rows to the text variable (will be sent to PrintMe)
        for row in range(rowcount):
            for col in range(colcount):
                if col == colcount - 1:
                    text += self.queueListCtrl.GetItemText(row, col) + '\n'
                else:  # Get contents of the queue
                    text += f'{self.queueListCtrl.GetItemText(row, col):{self.getSpacing(col)}} '
        PrintMe.printPreview(self, text)  # Send text to be rendered in the preview
    # Print Event Handler
    def print_OnClick(self, event):
        text = 'ID    NAME         COMPLETED BY DATE/TIME           CATEGORY        PRIORTY    STATUS      HIDE\n' \
               '----- ------------ ------------ ------------------- --------------- ---------- ----------- ----\n'
        # Get row and column count
        rowcount = self.queueListCtrl.GetItemCount()
        colcount = self.queueListCtrl.GetColumnCount()
        # Write rows to the text variable (will be sent to PrintMe)
        for row in range(rowcount):
            for col in range(colcount):
                if col == colcount - 1:
                    text += self.queueListCtrl.GetItemText(row, col) + '\n'
                else:  # Get contents of the queue
                    text += f'{self.queueListCtrl.GetItemText(row, col):{str(int(self.getSpacing(col)) + 1)}}'
        PrintMe.print(self, text)  # Send text to printer

class HelpMenu(wx.MiniFrame):
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(21, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        HelpLabel = wx.StaticText(panel, -1, 'Help')
        HelpLabel.SetFont(font)
        sizer.Add(HelpLabel, 0, wx.CENTER)
        HelpText = wx.StaticText(panel, -1, 'Direct any issues/questions to one of the following:')
        sizer.Add(HelpText, 0, wx.CENTER)
        sizer.AddSpacer(20)
        HelpDetail1 = wx.StaticText(panel, -1, 'Email: support@stickyhamster.com')
        sizer.Add(HelpDetail1, 0, wx.CENTER)
        HelpDetail2 = wx.StaticText(panel, -1, 'Call: 417-123-4567')
        sizer.Add(HelpDetail2, 0, wx.CENTER)
        HelpDetail3 = wx.StaticText(panel, -1, 'Office: Caleb Smith, Plaster Hall 208')
        sizer.Add(HelpDetail3, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        self.EmptyText = wx.StaticText(panel, -1)
        sizer.Add(self.EmptyText, 0, wx.CENTER)
        panel.SetSizerAndFit(sizer)
        self.QueryDBStatus()

    def QueryDBStatus(self):
        query = Query()
        sql = "SELECT * FROM User WHERE userId=1"
        result = query.genericQuery(sql, False)
        if result != 1:
            self.EmptyText.SetLabel('Database is up.')
        else:
            self.EmptyText.SetLabel('Database is down. Contact IT.')



