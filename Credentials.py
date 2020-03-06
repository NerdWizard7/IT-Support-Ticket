import hashlib
from DB import Query

class Credentials:
    @staticmethod
    def passwordHasher(username, passwd):
        query = Query()
        shaObj = hashlib.sha256()
        shaObj.update(passwd.envcode())
        result = query.userValidate(username, shaObj.hexdigest())
        if result == 0:
            return 0
        elif result == 1:
            return "User entered an incorrect password"
        else:
            "User entered an incorrect username"