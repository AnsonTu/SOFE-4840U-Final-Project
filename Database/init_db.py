import MySQLdb
import cPickle as pickle
import sys
import rsa
sys.path.insert(0, r'/home/musselman/Downloads/Web-based-secure-purchase-order-master/Database')
from Credentials import * 

# Function to generate key pairs.
def key_generation(email, password):
     (pub, priv) = rsa.newkeys(2048) # Generate key pair of size 2048.
     pu = pickle.dumps(pub) # Set public key string.
     pr = pickle.dumps(priv) # Set private key string.
     db = MySQLdb.connect(host = "localhost", user = "root", passwd = "root")
     cursor = db.cursor()
     cursor.execute("""use Simple_Kerberos""")
     cursor.execute("""INSERT INTO Credential VALUES (%s,%s,%s)""",(email, password, pr)) # Write the pre made credentials for the depts and the keys.
     db.commit()
     cursor.execute("""INSERT INTO PU_Directory VALUES (%s,%s)""",(email, pu)) # Same as other insert, but just writing the email and public key.
     db.commit()
     cursor.close()
     db.close() 

# Database initialization
db = MySQLdb.connect(host = "localhost", user = "root", passwd = "root")
cursor = db.cursor()
cursor.execute("""Create database Simple_Kerberos""")
cursor.execute("""use Simple_Kerberos""")

# Table creation where the keys and login creds will be stored.
cursor.execute("""CREATE TABLE Credential (Email varchar(255), Password varchar(255), PR varchar(5000))""")       
cursor.execute("""CREATE TABLE PU_Directory (Email varchar(255), PU varchar(5000))""")

# Call key gen functions to generate the key pairs for each dept.
key_generation(Purchase_Email, Purchase_Password)
key_generation(Super_Email, Super_Password) 
key_generation(Order_Email, Order_Password)
cursor.close()
db.close()
