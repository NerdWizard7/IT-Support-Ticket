class ListFormat:
    @staticmethod
    def listwriter(context, list):
        # Control Highlighting based on row values
        context.GetListCtrl().DeleteAllItems()
        for item in list:
            if item[:][6] == b'\x01':  # If Hidden is marked True...
                tup = item[6:] + ('True',) + item[:7]
                context.GetListCtrl().Append(tup)  # Append the item...
                context.GetListCtrl().SetItemTextColour(context.GetListCtrl().GetItemCount() - 1, 'Light Grey')  # Grey it out
            elif item[:][5] != 'Submitted':
                status = item[:][5]
                context.GetListCtrl().Append(item[:])
                if status == 'Completed':
                    context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Lime Green')
                elif status == 'In Progress':
                    context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Yellow')
                elif status == 'Halted':
                    context.GetListCtrl().SetItemBackgroundColour(context.GetListCtrl().GetItemCount() - 1, 'Red')
            else:
                tup = item[6:] + ('False',) + item[:7]
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

