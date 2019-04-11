import sys
import random

import psycopg2


conn = psycopg2.connect(database = "portal")
cur = conn.cursor()

# -------------- #
def user_program():
    user_email = input("User Email: ")
    user_id = input("User ID: ")
    cur.execute("SELECT * FROM users WHERE email = %s AND id = %s", (user_email,user_id))
    userdata = cur.fetchone()
    if userdata is not None:
        print(f"The email or ID is already in use.\n(Hint:{userdata})")
        return "non-unique user"
    user_password=""
    for i in range (1, 8):
      # We need 3 sides so you know what
      triforce = random.choice(['Courage', 'Wisdom', 'Power'])
      if triforce == 'Courage':
        # Add a lowercase one
        user_password += chr(random.randrange(97, 97 + 26))
      elif triforce == 'Wisdom':
        # Add an uppercase one
        user_password += chr(random.randrange(65, 65 + 26))
      else:
        # Add a number
        user_password += chr(random.randrange(48, 48 + 9))

    print(f"User {user_email}'s password is {user_password}")
    user_role= input("User Role (student/teacher): ")
    try:
        cur.execute("INSERT INTO users (id, email, password, role) VALUES(%s, %s, %s, %s)", (user_id, user_email, user_password, user_role))
        conn.commit()
        print(f"Added user {user_id}.")
        return "user added"
    except:
        print("User could not be added. Please make sure you are connected to the proper database. Check line 7 for details.")
        return "database error"

    will_loop = input("Add another user? Yes/No: ")
    if will_loop.lower() == "yes" or will_loop.lower() == "y":
        loop_program = True
        print("-"*10)
        return "Function exit."
    else:
        loop_program = False
        print("Exiting.")
        print("-"*10)
        sys.exit(1)

loop_program= True

while loop_program == True:
    user_program()
