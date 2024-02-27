import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from user_management import Users


user_id = int(sys.argv[1])

try:
    user = Users.get_user_by("id", user_id)
    if user != {}:
        print("Remove all data (includes their transaction log) of the following user?")
        print(user)
        print("Type (yes/no): ")
        input = input()
        if input in ["y", "yes"]:
            Users.rm_user(user_id)
            print(f"Removed user with ID {user_id}")
        elif input not in ["n", "no"]:
            print("Unvalid input")
            exit(0)
    else:
        print(f"User with ID {user_id} doesn't exist!")
except Exception as e:
    print(e)