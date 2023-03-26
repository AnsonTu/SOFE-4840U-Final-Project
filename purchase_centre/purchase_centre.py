from flask import Flask, request, render_template,redirect,url_for
import rsa
import hashlib
import MySQLdb
import os
import sys
import cPickle as pickle
sys.path.insert(0, r'/home/musselman/Downloads/SOFE-4840U-Final-Project-main/Database')
#sys.path.insert(0, "/home/musselman/Downloads/SecProj")
from Credentials import *
from items import item
from db_handler import *
from email_handler import send_email_super_orderdept

# Initalizing globals.
LEN_OF_KEY = 2048
EMAIL = ""
PASSWORD = ""
PURCH_ORD = ""


# Costs of the offered items.
printer = item(85)
tape_6rolls = item(10)
laser_toner_cart = item(80)
office_chair = item(300)
tablet = item(500)
laptop = item(1000)
thumbdrive64 = item(15)
deskfan = item(20)
usbhub = item(25)

app = Flask(__name__)

# Function that writes the now encrypted order request, and saves it as a file which will be sent later on.
def write_encrypt_order(order_cont):
    print(order_cont)
    e_file = open ("cust_PO.txt", "w")
    e_file.write(order_cont)
    e_file.close()

# Function that generates the encrytped order request that is signed with the user's private key, and encrypted with order dept and supervisor public keys for each.
def email_atta_gen(msg, priv, pub):
    global LEN_OF_KEY
    cust_sig = rsa.sign(msg, priv, 'MD5') # Sign the order, hash using MD5.
    N = 2048 / 8 # Convert to bytes.
    encrypted_order = rsa.encrypt(msg.encode('utf8'), pub)+"...."+rsa.encrypt(cust_sig[0:N-11], pub)+"...."+rsa.encrypt(cust_sig[N-11:], pub) # Concat with 4 .s so workable.
    return encrypted_order
   
# Function that gets the public keys of supervisor, and order dept, gets the email data, and sends the email to the supervisor and order dept.
def po_operation():
    global PURCH_ORD, LEN_OF_KEY
    cust_pr = fetch_pr(EMAIL)
    super_pu = fetch_pu(Super_Email)
    order_pu = fetch_pu(Order_Email)
    super_encrypt_file = email_atta_gen(PURCH_ORD, cust_pr, super_pu)
    order_encrypt_file = email_atta_gen(PURCH_ORD, cust_pr, order_pu)
    write_encrypt_order(super_encrypt_file)
    send_email_super_orderdept(Super_Email)
    write_encrypt_order(order_encrypt_file)
    send_email_super_orderdept(Order_Email)

# Function to affirm the requested order.
@app.route('/order_request', methods = ['POST', 'GET'])
def order_request(): 
    if request.method == 'POST':
       if (request.form['Confirm'] == 'Confirm'): 
            pid = os.fork()
            if (pid == 0):
                po_operation()     
            return render_template('request_confirmed.html')
       if (request.form['Back'] == 'Back'):
            return redirect(url_for('PO_gen'))

# Function to display if the user entered wrong password for an existing email while logging in.
@app.route('/incorrect_pass', methods = ['POST', 'GET'])
def incorrect_pass():
    print ("incorrect_pass")
    return render_template('index.html')


# Function to fetch the order request the user made, this will be sent via email to other depts.
@app.route('/PO_gen', methods = ['POST', 'GET'])
def PO_gen():
    print(EMAIL)
    if request.method == 'POST': 
        global PURCH_ORD
        printer.quantity = int(request.form['printerq'])
        tape_6rolls.quantity = int(request.form['tape_6rollsq'])
        laser_toner_cart.quantity = int(request.form['laser_toner_cartq'])
        office_chair.quantity = int(request.form['office_chairq'])
        tablet.quantity = int(request.form['tabletq'])
        laptop.quantity = int(request.form['laptopq'])
        thumbdrive64.quantity = int(request.form['thumbdrive64q'])
        deskfan.quantity = int(request.form['deskfanq'])
        usbhub.quantity = int(request.form['usbhubq'])
        printer.total = printer.quantity * printer.cost
        tape_6rolls.total = tape_6rolls.quantity * tape_6rolls.cost
        laser_toner_cart.total = laser_toner_cart.quantity * laser_toner_cart.cost
        office_chair.total = office_chair.quantity * office_chair.cost
        tablet.total = tablet.quantity * tablet.cost
        laptop.total = laptop.quantity * laptop.cost
        thumbdrive64.total = thumbdrive64.quantity * thumbdrive64.cost
        deskfan.total = deskfan.quantity * deskfan.cost
        usbhub.total = usbhub.quantity * usbhub.cost
        
        total_price = printer.total + tape_6rolls.total + laser_toner_cart.total + office_chair.total + \
        tablet.total + laptop.total + thumbdrive64.total + deskfan.total + usbhub.total
        
        # Below in the creation of the PO that the customer is requesting.
        PURCH_ORD = "Email:" + EMAIL + "\nPrinter(" + str(printer.quantity) + " #): $" + \
        str(printer.total) + "\nTape (6 rolls)(" + str(tape_6rolls.quantity) + " #): $" + str(tape_6rolls.total) \
        + "\noffice_chair(" + str(office_chair.quantity) + " #): $" + str(office_chair.total) + "\nTablet(" + str(tablet.quantity) \
        + " #): $" + str(tablet.total) + "\nLaptop(" + str(laptop.quantity) + " #): $" + str(laptop.total) + \
        "\nThumbdrive 64GB(" + str(thumbdrive64.quantity) + " #): $" + str(thumbdrive64.total) + \
        "\nDesk Fan(" + str(deskfan.quantity) + " #): $" + str(deskfan.total) + \
        "\nUSB Hub(" + str(usbhub.quantity) + " #: $" + str(usbhub.total) + "\nTotal Price = " + str(total_price)
        
        return render_template('order_request.html', printert = printer.total, tape_6rollst = tape_6rolls.total, laser_toner_cartt = laser_toner_cart.total, \
        office_chairt = office_chair.total, tablett = tablet.total, laptopt = laptop.total, thumbdrive64t = thumbdrive64.total, deskfant = deskfan.total, \
        usbhubt = usbhub.total, amount = total_price, printerq = printer.quantity, tape_6rollsq = tape_6rolls.quantity, laser_toner_cartq = laser_toner_cart.quantity, \
        office_chairq = office_chair.quantity, tabletq = tablet.quantity, laptopq = laptop.quantity, thumbdrive64q = thumbdrive64.quantity, deskfanq = deskfan.quantity, \
        usbhubq = usbhub.quantity)
        
    return render_template('PO_gen.html')

# Function that creates the PU and PR key pair, and saves them to the required DB tables. Also helper function.
@app.route('/write_to_dbs')
def write_to_dbs():
   global EMAIL, PASSWORD
   (db, cursor) = db_conn()
   (pub, priv) = rsa.newkeys(LEN_OF_KEY)
   pu = pickle.dumps(pub)
   pr = pickle.dumps(priv)
   cursor.execute("""INSERT INTO Credential VALUES (%s,%s,%s)""", (EMAIL, PASSWORD, pr))
   db.commit()
   cursor.execute("""INSERT INTO PU_Directory VALUES (%s,%s)""", (EMAIL, pu))
   db.commit()
   cursor.close()
   db.close()
   return redirect(url_for('PO_gen'))

# This function does both registration and login in one, thanks to the helper function above.
@app.route('/verify')
def check_pass():
   global EMAIL, PASSWORD
   (db, cursor) = db_conn()
   cursor.execute("""select Password from Credential where Email=%s""", (EMAIL,))
   password = cursor.fetchone()
   cursor.close()
   db.close()
   if (password == None):
       return redirect(url_for('write_to_dbs'))
   print(password[0])
   print(PASSWORD)
   
   # Check for wrong password entered.
   if  (password[0] == PASSWORD):
       return redirect(url_for('PO_gen'))
   return redirect(url_for('incorrect_pass'))
    

# Will launch the page for login prompt from the user.
@app.route('/', methods = ['POST', 'GET'])
def login():
    print(Super_Email)
    global EMAIL, PASSWORD
    if request.method == 'POST':
        EMAIL =  request.form['EmailID']                   
        PASSWORD = request.form['Password']
	print("EMAIL FROM INDEX: " + EMAIL)
	print("PASSWORD FROM INDEX: " + PASSWORD)
        return redirect(url_for('check_pass'))
    return render_template('index.html')

# Flask app running.
if __name__ == '__main__':
    app.debug = True
    app.run()
