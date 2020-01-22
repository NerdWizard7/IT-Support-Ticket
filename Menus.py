import wx
import wx.lib.editor as editor
from PrintHandler import PrintMe, PrintFormat
from DB import Query, DBManager
import json
from Format import ListFormat, Sorter
import sqlparse

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
        sql = f"SELECT Notes " \
              f"FROM {schema}.notes " \
              f"WHERE ID = {id}"
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
            sql = f"INSERT INTO {schema}.notes " \
                  f"VALUES (%s, %s)"
            val = (f"{self.id}", f"{json.dumps(text)}")  # Values to be inserted
            if query.insertData(sql, val, False) == 0:  # Make query
                msg = wx.MessageBox('Notes Added Successcully!', 'Success!')
            else:
                msg = wx.MessageBox('Something went wrong. Contact a system administrator immediately.',
                                    'Error')
        else:  # Not a new note
            # Set up conditions for the update method in Query class
            condition = f"ID = {self.id}"
            set = f"Notes = '{json.dumps(text)}'"
            dbname = f'{schema}.notes'
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

