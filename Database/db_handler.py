import MySQLdb
import cPickle as pickle

# Function to create a connection with the DB.
def db_conn(): # open_db
    db = MySQLdb.connect(host = "localhost", user = "root", passwd = "root", db = "Simple_Kerberos") # Database connection
    cursor = db.cursor() # Setting cursor for the database.
    return (db,cursor)

# Function to fetch the private key given an email from the database.
def fetch_pr(email): # get_privatekey
    (db, cursor) = db_conn()
    cursor.execute("""select PR from Credential where Email=%s""",(email,))
    PR_str = cursor.fetchone()
    pr = pickle.loads(PR_str[0]) # Change the PR to object, so it is workable. 
    cursor.close()
    db.close()
    return pr

# Function to fetch the public key given an email from the database.
def fetch_pu(email): # get_publickey
    (db, cursor) = db_conn() 
    cursor.execute("""select PU from PU_Directory where Email=%s""",(email,))
    PU_str = cursor.fetchone()
    pu = pickle.loads(PU_str[0]) # Change the PU to object.
    cursor.close()
    db.close()
    return pu
