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
        else:
            return "Username is incorrect"

    @staticmethod
    def getUserId(username):
        query = Query()
        sql = f"SELECT userId FROM User WHERE username = {username}"
        userId = query.genericQuery(sql, False)
        return userId