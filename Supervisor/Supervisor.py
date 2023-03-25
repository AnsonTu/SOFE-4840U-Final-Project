from flask import Flask, request, render_template, redirect, url_for
import MySQLdb
import os
import rsa
import cPickle as pickle
import sys
sys.path.insert(0, "/home/musselman/Downloads/SecProj/Database")
sys.path.insert(0, "/home/musselman/Downloads/SecProj")
from email_handler import send_email_to_orderdept
from Credentials import *
from db_handler import *
from werkzeug.utils import secure_filename
import os
import hashlib

LOC_OF_UPLOAD = '/home/musselman/Downloads'
EXTEN = set(['txt'])

# Initializing globals.
LEN_KEY_GEN = 2048
EMAIL_ADDRESS = ""
PASS = ""
super_PO = ""
cust_PO = ""

app = Flask(__name__)
app.config['LOC_OF_UPLOAD'] = LOC_OF_UPLOAD

# Generates the signed message PO.
def fetch_signed_message():
    with open('/home/musselman/Downloads/cust_PO.txt', 'r') as custpo_file:
        file_cont = custpo_file.read()
    attr = file_cont.split("....") # Want to split whenever .... occurs, this split the message into more workable segments.
    pr_super = fetch_pr(Super_Email) # Get the pr of system supervisor.
    order_msg = rsa.decrypt(attr[0], pr_super) # Decrypt the order message.
    order_msg = order_msg.decode('utf8') # Decode the message as to make readable by us.
    sig_seg_1 = rsa.decrypt(attr[1], pr_super) # Sign message segment 1 with supervisor pr.
    sig_seg_2 =  rsa.decrypt(attr[2], pr_super) # Sign message segment 2 with supervisor pr.
    sig_super = sig_seg_1 + sig_seg_2 # Combine the previous signatures.
    
    # Writing the order message.
    f_super = open ("super_PO.txt","w")
    f_super.write(order_msg)
    f_super.close()
    
    return (order_msg, sig_super)

# Function that extracts the customer email that made the order request.
def fetch_cust_email_addr(po_message):
    attr_1 = po_message.split("Email:")
    attr_2 = attr_1[1].split("\n")
    return (attr_2[0])

# Function to write and save the encrypted supervisor po.
def write_encrypt_message(in_message):
    f_encrypt_msg = open ("super_PO.txt","w")
    f_encrypt_msg.write(in_message)
    f_encrypt_msg.close()

# Function to create the email attatchment sent to the order dept.
def fetch_email_attatch(po_message, pr_cust, pu):
    global LEN_KEY_GEN
    sig_cust = rsa.sign(po_message, pr_cust, 'MD5') # Hash using MD5, and the pr of the cutomer making the order.
    N = 2048 / 8 # Convert to bytes.
    
    # Encrypt the message that will be emailed to the order dept.
    enc_message = rsa.encrypt(po_message.encode('utf8'), pu)+"...."+rsa.encrypt(sig_cust[0:N-11], pu)+"...."+rsa.encrypt(sig_cust[N-11:], pu)
    return enc_message
   
# Function to forward the order to the order dept. 
def po_operations():
    global LEN_KEY_GEN
    pr_cust = fetch_pr(EMAIL_ADDRESS)
    order_pu = fetch_pu(Order_Email)
    with open('super_PO.txt', 'r') as superpo_file:	
        superpo_message = superpo_file.read()
        
    # Send encrypted signed message to order dept.
    crypto_orderdept = fetch_email_attatch(superpo_message, pr_cust, order_pu)
    write_encrypt_message(crypto_orderdept)
    send_email_to_orderdept(Order_Email)

# Display supervisor approval page after email is send 
@app.route('/approved', methods = ['POST','GET'])
def approved():
    return render_template('approved.html')

# Function to output the receipt of the purchase order.
@app.route('/po_receipt', methods = ['POST','GET'])
def po_receipt(): 
    global cust_PO
    if request.method == 'POST':
        if(request.form['Verify & Sign'] == 'Verify & Sign'):
	    print("TEST")
            po_operations()
        return render_template('approved.html')
    return render_template('po_receipt.html')

# Function to verify and confirm the order request, through the signature and po contents. Receipt of po is displayed afterwards.
@app.route('/validate_order', methods=['POST','GET'])
def validate_order():
    order_msg, super_sig = fetch_signed_message() 	
    user_email = fetch_cust_email_addr(order_msg)

    public = fetch_pu(user_email)
    print(order_msg)
    if request.method == 'POST':
        print("TEST: ACCESS") # Debugging
        if(rsa.verify(order_msg, super_sig, public)):
            print ("Super visor signature checks out!!!")
    	return render_template('po_receipt.html', message_html = order_msg)
    return render_template('po_receipt.html', message_html = order_msg)

# Function to get the uploaded PO file from the supervisor and save it an the predefined dir of specified in LOC_OF_UPLOAD.
@app.route('/po_auth', methods=['POST','GET'])
def po_auth():
    if request.method == 'POST':
        super_po_file = request.files['super_po_file']
        if super_po_file:
            super_file_name = secure_filename(super_po_file.filename)
            super_po_file.save(os.path.join(app.config['LOC_OF_UPLOAD'], super_file_name))
            return redirect(url_for('validate_order'))
    return render_template('po_auth.html')

# Function when the supervisor enters the incorrect credentials.
@app.route('/incorrect_creds',methods=['GET'])
def incorrect_creds():
    return render_template('login.html')

# Helper function to check login credentials.
@app.route('/verify_creds')
def verify_creds():
    global EMAIL_ADDRESS, PASS
    if (EMAIL_ADDRESS == Super_Email and PASS == Super_Password):
        return redirect(url_for('po_auth'))
    else:
        return redirect(url_for('incorrect_creds'))    

#Login Page, enter email and password
@app.route("/",methods=['POST','GET'])
def home():
    global EMAIL_ADDRESS,PASS
    if request.method == 'POST':
        EMAIL_ADDRESS = request.form['EmailID']
        PASS = request.form['Password']
        return redirect(url_for('verify_creds'))
    return render_template('login.html')        



if __name__ == '__main__':
    app.debug == True
    app.run()
