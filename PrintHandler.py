import wx

FONTSIZE = 10


class Print(wx.Printout):
    # Default constructor for Print
    # The methods in this class are all implementations of abstract methods in wx.Printout.
    # Plenty of documentation already exists online for these, so it will be left out here
    def __init__(self, text, title, margins):
        wx.Printout.__init__(self, title)
        self.lines = text.split('\n')
        self.margins = margins

    def HasPage(self, page):
        return page <= self.numPages

    def GetPageInfo(self):
        return (1, self.numPages, 1, self.numPages)

    def CalculateScale(self, dc):
        ppiPrinterX, ppiPrinterY = self.GetPPIPrinter()
        ppiScreenX, ppiScreenY = self.GetPPIScreen()
        logScale = float(ppiPrinterX) / float(ppiScreenX)

        pw, ph = self.GetPageSizePixels()
        dw, dh = dc.GetSize()
        scale = logScale * float(dw) / float(pw)
        dc.SetUserScale(scale, scale)
        self.logUnitsMM = float(ppiPrinterX) / (logScale * 25.4)

    def CalculateLayout(self, dc):
        topLeft, bottomRight = self.margins
        dw, dh = dc.GetSize()
        self.x1 = topLeft.x * self.logUnitsMM
        self.y1 = topLeft.y * self.logUnitsMM
        self.x2 = (dc.DeviceToLogicalXRel(dw) - bottomRight.x * self.logUnitsMM)
        self.y2 = (dc.DeviceToLogicalYRel(dh) - bottomRight.y * self.logUnitsMM)
        self.pageHeight = self.y2 - self.y1 - 2 * self.logUnitsMM
        font = wx.Font(FONTSIZE, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        dc.SetFont(font)
        self.lineHeight = dc.GetCharHeight()
        self.linesPerPage = int(self.pageHeight / self.lineHeight)

    def OnPreparePrinting(self):
        dc = self.GetDC()
        self.CalculateScale(dc)
        self.CalculateLayout(dc)
        self.numPages = len(self.lines) / self.linesPerPage
        if len(self.lines) % self.linesPerPage != 0:
            self.numPages += 1

    def OnPrintPage(self, page):
        dc = self.GetDC()
        self.CalculateScale(dc)
        self.CalculateLayout(dc)

        line = (page - 1) * self.linesPerPage
        x = self.x1 + self.logUnitsMM
        y = self.y1 + self.logUnitsMM
        while line < (page * self.linesPerPage):
            dc.DrawText(self.lines[line], x, y)
            y += self.lineHeight
            line += 1
            if line >= len(self.lines):
                break
        return True
# End Print Class

class PrintMe:
    # This class contains the static print methods that set up print data for the Print class.

    # Page Setup Menu Item Event Handler
    @staticmethod
    def pageSetup(ref):
        data = wx.PageSetupDialogData()  # Initialize data as a PageSetupDialogData object
        data.SetPrintData(ref.pdata)  # Set the print data to self.pdata (declared at beginning)
        data.SetDefaultMinMargins(True)  # Set default minimum margins to True
        data.SetMarginTopLeft(ref.margins[0])  # Setup margins
        data.SetMarginBottomRight(ref.margins[1])
        dlg = wx.PageSetupDialog(ref, data)  # Open Page Setup Dialog
        if dlg.ShowModal() == wx.ID_OK:  # If the user clicks OK...
            data = dlg.GetPageSetupData()  # Save settings in data
            ref.pdata = wx.PrintData(data.GetPrintData())  # set self.pdata to the data entered in the dlg
            ref.pdata.SetPaperId(data.GetPaperId())  # Set paper type from the dlg
            ref.margins = (data.GetMarginTopLeft(),
                            data.GetMarginBottomRight())  # Margins from the dlg
        dlg.Destroy()

    # Print Preview Event Handler
    @staticmethod
    def printPreview(ref, text):
        data = wx.PrintDialogData(ref.pdata)  # Initialize data as a PrintDialogData object
        printout1 = Print(text, "title", ref.margins)  # Set printout 1 and 2 to display the text
        printout2 = print(text, "title", ref.margins)
        preview = wx.PrintPreview(printout1, printout2, data)  # Set Preview Data
        if not preview.IsOk():  # If not preview.Ok (something went wrong)
            wx.MessageBox("Unable to create Print Preview!", "Error")  # Display an error window
        else:  # Everything worked
            frame = wx.PreviewFrame(preview, ref, "Print Preview",
                                    pos=ref.GetPosition(), size=ref.GetSize())  # Render the preview
            frame.Initialize()  # Initialize the frame
            frame.Show()  # Show the window

    # Print Event Handler
    @staticmethod
    def print(ref, text):
        data = wx.PrintDialogData(ref.pdata)  # Initialize data as a PrintDialogData object
        printer = wx.Printer(data)  # Deglare printer as a Printer object
        printout = Print(text, "Title", ref.margins)  # Call Print class to handle the print job
        useSetupDialog = True  # Tell the window to use the seutp dialog
        # If there is a print error...
        if not printer.Print(ref, printout, useSetupDialog) and printer.GetLastError() == wx.PRINTER_ERROR:
            wx.MessageBox("There was a problem printing.\n"
                          "Make sure your printer is set up correctly and try again.",
                          "Printing Error", wx.OK)  # Print error window
        else:  # No Error
            data = printer.GetPrintDialogData()  # Store PrintDialogData from window in data
            ref.pdata = wx.PrintData(data.GetPrintData())  # Write settings to self.pdata
        printout.Destroy()
# End PrintMe Class

class PrintFormat:

    __printHeader = 'ID    NAME         DATE/TIME           CATEGORY        PRIORTY    STATUS      HIDE\n' \
                           '----- ------------ ------------------- --------------- ---------- ----------- ----\n'

    @staticmethod
    def getPrintHeader():
        return PrintFormat.__printHeader

    @staticmethod
    # This method sets up print spacing so each column is formatted correctly
    def getSpacing(col):
        # Sets up print spacing.
        # Called every time a new column is written to the page
        if col == 0:
            return '5'
        elif col == 1:
            return '12'
        elif col == 2:
            return '19'
        elif col == 3:
            return '15'
        elif col == 4:
            return '10'
        elif col == 5:
            return '11'
        else:
            return '4'
