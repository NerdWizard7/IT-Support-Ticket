from Credentials import Credentials

class ListFormat:
    @staticmethod
    def listwriter(context, list):
        # Control Highlighting based on row values
        context.GetListCtrl().DeleteAllItems()
        for item in list:
            # Really dumb way to change b'\x01' to 'Yes', and 'No' respectively...

            if len(item[:]) == 7:
                tup = item[:6] + ('Yes',) if item[:][6] == b'\x01' or item[:][6] == 'Yes' else item[:6] + ('No',)
                print(tup)
                if tup[6] == 'Yes':  # If Hidden is marked True...
                    context.GetListCtrl().Append(tup)  # Append the item...
                    context.GetListCtrl().SetItemTextColour(context.GetListCtrl().GetItemCount() - 1, 'Light Grey')  # Grey it out
                elif tup[5] == 'Submitted':  # fifth index (job status) is 'Submitted'
                    status = tup[5]
                    context.GetListCtrl().Append(tup)
                    context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Light Blue')
                elif tup[5] != 'Submitted':  # fifth index (job status) is 'Submitted'
                    status = tup[5]
                    context.GetListCtrl().Append(tup)
                    if status == 'In Progress':  # job Status is 'In Progress'
                        context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Lime Green')
                    elif status == 'Halted':# job Status is 'Halted'
                        context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Yellow')
                else:
                    context.GetListCtrl().Append(tup)  # Append the Item with normal background
            elif len(item[:]) == 8:  # Has CompletedBy field
                tup = item[:7] + ('Yes',) if item[:][7] == b'\x01' or item[:][7] == 'Yes' else item[:7] + ('No',)
                username = Credentials.getUsername(tup[2]) if tup[2] != None else '----'
                tup = tup[:2] + (username,) + tup[3:]
                print(tup)
                if tup[7] == 'Yes':  # If Hidden is marked True...
                    context.GetListCtrl().Append(tup)  # Append the item...
                    context.GetListCtrl().SetItemTextColour(context.GetListCtrl().GetItemCount() - 1, 'Light Grey')  # Grey it out
                elif tup[6] != 'Submitted':  # fifth index (job status) is 'Submitted'
                    status = tup[6]
                    context.GetListCtrl().Append(tup)
                    if status == 'In Progress':  # job Status is 'In Progress'
                        context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Lime Green')
                    elif status == 'Halted':# job Status is 'Halted'
                        context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Yellow')
                else:
                    context.GetListCtrl().Append(tup)  # Append the Item with normal background

class Sorter:
    @staticmethod
    def sort(context, colIndex):
        if colIndex == 0:
            context.refreshDB()
        else:
            context.refreshDB()
            print(f'Entered Sort on column {colIndex}')
            allrows = []  # Create allrows list
            rowcount = context.GetListCtrl().GetItemCount()  # Get row count
            colcount = context.GetListCtrl().GetColumnCount()  # Get column count
            for row in range(0, rowcount):  # For each row from 0 to row count...
                singlerow = ()  # Set singlerow tuple to ()
                for col in range(0, colcount):  # For every col from 0 to column count...
                    item = context.GetListCtrl().GetItemText(row, col)  # Set item equal to the text in that spot
                    singlerow = singlerow + (f'{item}',)  # Add that text to the singlerow tuple
                allrows.append(singlerow)  # Append the tuple to the allrows list
            # Sort the allrows list
            for i in range(rowcount):  # For every row from 0 to row count...
                for j in range(0, rowcount-i-1):  # For every row in the range of rows that haven't been sorted yet...
                    # If colIndex in the tuple is greater than the next one...
                    if (allrows[j][colIndex]) > (allrows[j + 1][colIndex]):
                        allrows[j], allrows[j + 1] = allrows[j + 1], allrows[j]  # Swap them
            ListFormat.listwriter(context, allrows)  # Call listwriter to rewrite the listctrl

