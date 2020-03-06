import pymysql
import traceback
from pathlib import Path
import os
import sys

platform = sys.platform  # Set platform to the string value returned by sys.platform (win32, darwin, linux, cigwin)

# OS detection logic
if platform == 'win32':  # Computer is a windows machine
    dir = rf'{Path.home()}\AppData\Local\ITSupportClient'  # Store config files in AppData\Local\...
    filePath = rf'{dir}\dbconfig.cfg'  # Set the filepath with a \ for windows
else:  # Computer is a unix or macOS machine
    dir = rf'{Path.home()}/ITSupportClient'  # Store config files in user's home directory
    filePath = rf'{dir}/dbconfig.cfg'  # Set the filepath with a / for macOS / Unix

class DBManager():
    # Gets all of the db settings from the dbconfig.cfg file. This is called when the program loads
    @staticmethod
    def load():
        global dir
        global filePath
        if os.path.isdir(dir) and os.path.isfile(filePath):  # If the directory exists...
            if os.stat(filePath).st_size > 0:
                with open(filePath) as file:  # Open the config file
                    data = []  # Make data list
                    [data.append(line) for line in file]  # Append each line in the file to the list
                    data = [x.strip() for x in data]  # Strip the newline characters
                return data  # Return the list
            else:
                data = ['','','','']
                return data
        else:  # File path doesn't exist
            try:
                os.makedirs(dir)  # Make the path
            except:  # Path existed, but file didn't
                print('Path existed, making file')
            newfile = open(filePath, 'w')  # Create the config file
            newfile.close()
            data = ['','','','']
            return data  # Return the list

    # Sets (overwrites) the dbconfig.cfg file any time a user updates the values in the dbsettings menu
    @staticmethod
    def save(host, user, passwd, db):
        global dir
        global filePath
        #dir = rf'{Path.home()}\AppData\Local\BMISupportClient'
        with open(filePath, 'w+') as file:  # Open the config file
            data = [host, user, passwd, db]  # Create data list full of db settings
            file.truncate()  # Truncate existing file
            for item in data:  # For each item in data list (host, user, passwd, and db)
                file.write(item + '\n')  # Write it to a new line in the file

# Set up Database Information
db = DBManager
data = db.load()

HOSTNAME = data[0]
USER = data[1]
PASSWD = data[2]
DB = data[3]
# ---------------------------

class Query:

    # TODO: Restructure all of these methods to fit the new database design

    # The following methods are responsible for creating the actual connection to the SQL server.
    # Each one of these methods does a slightly different thing. The genericQuery method can be
    # used for pretty much all of them, but some of them have special return types for error checking,
    # and call methods that are more specialized for the task.

    # Static method to insert new data into a given database table
    @staticmethod
    def insertData(sql, val, multi):
        # Try except block to catch SQL errors (they are common)
        try:
            mydb = pymysql.connect(host=HOSTNAME, user=USER, passwd=PASSWD)  # Create a new connector object
            with mydb:
                mycursor = mydb.cursor()  # Create a db cursor
                mycursor.execute(sql, val)  # Execute the query
                mydb.commit()  # Commit the statement
                # Close the connection
                mycursor.close()
            mydb.close()
            return 0
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            return 1

    # Static method to all records submitted by a given user
    @staticmethod
    def selectUser(uname):
        db = DBManager
        schema = db.load()[3]
        mydb = pymysql.connect(host=HOSTNAME, user=USER, passwd=PASSWD)
        with mydb:
            mycursor = mydb.cursor()
            sql = f"SELECT ID, Name, Date, Category, Priority, Status, Hidden " \
                  f"FROM {schema}.requests " \
                  f"WHERE Name = '{uname}' " \
                  f"AND Status != 'Completed'"
            mycursor.execute(sql)
            results = mycursor.fetchall()
            mydb.commit()
            mycursor.close()
        mydb.close()
        return results

    # Static method to get the description field of a database record when passed the ticket ID
    @staticmethod
    def getDescById(id):
        db = DBManager
        schema = db.load()[3]
        mydb = pymysql.connect(host=HOSTNAME, user=USER, passwd=PASSWD)
        with mydb:
            mycursor = mydb.cursor()
            sql = f"SELECT description FROM {schema}.Description WHERE ticketId = {id}"
            mycursor.execute(sql)
            description = mycursor.fetchall()
            mydb.commit()
            mycursor.close()
        mydb.close()
        return description

    # Static method to make a generic SQL query. You can pass this any SQL and it will run it
    @staticmethod
    # TODO: This method can likely stay the same. All others need changed.
    def genericQuery(sql, multi):
        schema = db.load()[3]
        try:
            mydb = pymysql.connect(host=HOSTNAME, user=USER, passwd=PASSWD)
            with mydb:
                mycursor = mydb.cursor()
                mycursor.execute(f'USE {schema};')
                if multi:
                    mycursor.execute(sql, True)
                else:
                    mycursor.execute(sql)
                result = mycursor.fetchall()
                mydb.commit()
                mycursor.close()
            mydb.close()
            print(result)
            return result
        except Exception as err:
            print(traceback.format_exc())
            print(err)
            return 1

    # Static method to update an existing database record
    @staticmethod
    def updateTable(db, set, cond):
        try:
            mydb = pymysql.connect(host=HOSTNAME, user=USER, passwd=PASSWD)
            with mydb:
                mycursor = mydb.cursor()
                sql = f"UPDATE {db} SET {set} WHERE {cond};"
                print(sql)
                mycursor.execute(sql)
                mydb.commit()
                mycursor.close()
            mydb.close()
            return 0
        except Exception as err:
            print(traceback.format_exc())
            print(err)
            return 1

    @staticmethod
    def userValidate(username, passwd):
        try:
            mydb = pymysql.connect(host=HOSTNAME, user=USER, passwd=PASSWD)
            with mydb:
                mycursor = mydb.cursor()
                sql=f'SELECT passwordHash FROM User WHERE username = {username}'
                mycursor.execute(sql)
                hash = mycursor.fetchall()
                if passwd == hash:  # User is real
                    return 0
                else:
                    return 1
        except Exception as err:
            print(traceback.format_exc())
            print(err)
            return 2


