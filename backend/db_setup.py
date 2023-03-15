import rsa
import MySQLdb
import pickle as pkl
from user_email_info import *

# Function to for the public private key pair generation.
def key_pair_gen(user_email, pswrd):
    (pu, pr) = rsa.newkeys(1024) # Generate pu pr key pair of size 1024. Should take 0.3s to 0.79s.
    pu_key = pkl.dumps(pu)
    pr_key = pkl.dumps(pr)

    # Database connection.
    key_database = MySQLdb.connect(host='localhost', user='root', passwd='')
    
    cursor = key_database.cursor()
    cursor.execute("""USE key_db""")
    cursor.execute("""INSERT INTO User_Credentials VALUES (%s,%s,%s)""",(user_email, pswrd, pr_key))
    key_database.commit()
    cursor.execute("""INSERT INTO PU_Key_Lookup VALUES (%s,%s)""", (user_email, pu_key))
    key_database.commit()
    cursor.close()
    key_database.close()

# Database creation execution.
key_database = MySQLdb.connect(host='localhost', user='root', passwd='')
cursor = key_database.cursor()
cursor.execute("""CREATE DATABASE key_db""")
cursor.execute("""USE key_db""")
cursor.execute("""CREATE TABLE User_Credentials (E_ID VARCHAR(255), User_Pswrd VARCHAR(255), PR VARCHAR(8191))""")
cursor.execute("""CREATE TABLE PU_Key_Lookup ( E_ID VARCHAR(255), PU(8191))""")

key_pair_gen(super_gmail, super_pass)
key_pair_gen(purch_gmail, purch_pass)
key_pair_gen(orderdept_gmail, orderdept_pass)

cursor.close()
key_database.close()