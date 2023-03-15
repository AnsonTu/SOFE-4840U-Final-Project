import MySQLdb
import pickle as pkl

# Connection to the key database.
def connect_to_database():
    key_database = MySQLdb.connect(host='localhost',user='root',passwd='',db='key_db')
    cursor = key_database.cursor()
    return(key_database, cursor)

# Retrieving the public key from the database.
def pu_retrieval(user_email):
    (key_database, cursor) = connect_to_database()
    cursor.execute("""SELECT PU FROM User_Credentials WHERE E_ID=%s""",(user_email,))
    fetch_pu = cursor.fetchone()
    pu = pkl.loads(fetch_pu[0])
    cursor.close()
    key_database.close()
    return pu


# Retrieving the private key from the database.
def pr_retrieval(user_email):
    (key_database, cursor) = connect_to_database()
    cursor.execute("""SELECT PR FROM PU_Key_Lookup WHERE E_ID=%s""", (user_email,))
    fetch_pr = cursor.fetchone()
    pr = pkl.loads(fetch_pr[0])
    cursor.close()
    key_database.close()
    return pr