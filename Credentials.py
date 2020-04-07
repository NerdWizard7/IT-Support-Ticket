import hashlib
from DB import Query

class Credentials:
    @staticmethod
    def passwordHasher(username, passwd):
        query = Query()
        shaObj = hashlib.sha256()
        shaObj.update(passwd.encode())
        print(shaObj.hexdigest())
        result = query.userValidate(username, shaObj.hexdigest())
        if result == 0:
            return 0
        elif result == 1:
            return 1
        elif result == 2:
            return "Password is incorrect"
        elif result == 3:
            return "Username is incorrect"
        else:
            return "That user account is disabled. Contact IT if this is an error."

    @staticmethod
    def passwordHash(passwd):
        shaObj = hashlib.sha256()
        shaObj.update(passwd.encode())
        if passwd != '':
            return shaObj.hexdigest()
        else:
            return 'NULL'

    @staticmethod
    def getUserId(username):
        query = Query()
        sql = f"SELECT userId FROM User WHERE username = '{username}'"
        userId = query.genericQuery(sql, False)
        return userId
