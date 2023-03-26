from flask import Flask, request, render_template, redirect, url_for
import sys
sys.path.insert(0, "/home/musselman/Downloads/SOFE-4840U-Final-Project-main/Database")
sys.path.insert(0, "/home/musselman/Downloads/SecProj")
import os
from Credentials import *
from email_handler import send_confirmation_email
from db_handler import *
import rsa
import MySQLdb
from flask_wtf import Form
from werkzeug.utils import secure_filename
from wtforms import StringField

LOC_OF_UPLOAD = '/home/musselman/Downloads'
EXTEN = set(['txt'])

app = Flask(__name__)
app.config['LOC_OF_UPLOAD'] = LOC_OF_UPLOAD

# Function to send confirmation that the user's order request is approved.
@app.route('/send_user_email', methods=['POST'])
def send_user_email():
    global uEmail	
    print("Send the user confirmation email")
    if request.method == 'POST':
        if(request.form and request.form['orderstatus']):
            status = request.form['orderstatus']
            print(status)
            send_confirmation_email(uEmail, status)
            print(status)
    return render_template('sent-confirm.html')

# Function to perform a check to make sure that the two supplied files have the same hash.
def auth_files(poContFile1, poContFile2):
     pr_1 = fetch_pr(Order_Email)
     u_hash_md5 = rsa.sign(poContFile1, pr_1, 'MD5')
     pr_2 = fetch_pr(Order_Email)
     super_hash_md5 = rsa.sign(poContFile2, pr_2, 'MD5')
     if (u_hash_md5 == super_hash_md5):
         return True
     else:
         return False

 # Function to verify the order.
def sig_verification(pt, st, str):
        id_of_email = fetch_id_email(pt, str)
        pu = fetch_pu(id_of_email)
        if (rsa.verify(pt, st, pu)):
            return True
        else:
            return False

# Function to fetch the email id that belongs to the supervisor.
def fetch_id_email(pt, str):
    global uEmail
    
    # Split and assign different (key, sig, email) values to vars.
    if (str == 'user'):
        attr1 = pt.split("Email:")
        attr2 = attr1[1].split("\n")
        uEmail = attr2[0]
        return (attr2[0])
    else:
        return Super_Email

# Decrypt the encrypted purchase order.
def po_decrypt(po_encrypt_cont):
        list = po_encrypt_cont.split("....") # Separate on every instance of ....
        pr = fetch_pr(Order_Email) # Fetching the order dept private key.
        po_cont = rsa.decrypt(list[0], pr) # Decrypt using private key of orderdepartment.
        po_cont = po_cont.decode('utf8') # Decoding the encoded po contents.
        index, st = 1, "" # Setting index, and signed text.
        
        # Decrypt the split signed po contents.
        for index in range(index, (len(list))):
            st += rsa.decrypt(list[index], pr)
        return po_cont, st

#  Verify using the decrypted message and signatures.
def verify_decryp_sign(po_encrypt_1, po_encrypt_2):
     # Getting the plaintext along with the signature of the order using both the user, and the supervisor.
     cust_po_cont, cust_signed_cont = po_decrypt(po_encrypt_1)
     super_po_cont, super_signed_cont = po_decrypt(po_encrypt_2)

     # Ensuring that both the user and supervisor are signed.
     cust_veri = sig_verification(cust_po_cont, cust_signed_cont, "user")
     super_veri = sig_verification(super_po_cont, super_signed_cont, "supervisor")
     flag_v = (cust_veri and super_veri)
     auth_status = auth_files(cust_po_cont, super_po_cont)
     if(flag_v and auth_status):
        return "Validation Success"
     else:
        return "Validation Failed"
        
# Function to read the contents of the PO files.
def read_po_files(input_file):
    try:
        if input_file:
            with open(os.path.join(app.config['LOC_OF_UPLOAD'], input_file)) as f_in:
                return f_in.read()
    except IOError:
        pass
    return "Error: Could not read your file!!!!"

# Upload and call for authentication
@app.route('/auth_po_contents', methods=['POST','GET'])
def auth_po_contents():
    if (request.method == 'GET'):
        return render_template('auth_po_contents.html')
    if request.method == 'POST':
        if (len(request.files) != 2):
            return render_template('upload_error.html')
        po_file_1 = request.files['po_file_1']
        po_file_2 = request.files['po_file_2']
        
        # File reading, along with dealing with file upload.
        f1 = secure_filename(po_file_1.filename)
        f2 = secure_filename(po_file_2.filename)
        po_file_1.save(os.path.join(app.config['LOC_OF_UPLOAD'], f1))
        po_file_2.save(os.path.join(app.config['LOC_OF_UPLOAD'], f2))
        po_encrypt_1 = read_po_files(f1)
        po_encrypt_2 = read_po_files(f2)
        verify_status = verify_decryp_sign(po_encrypt_1, po_encrypt_2)
	print(verify_status)
        final_res = ("The files: " + f1 + "\t"+" and " + f2 + " have been properly uploaded!!!!")
        return render_template('approve-reject.html', result = final_res, status = verify_status)

# Incorrect login information.
@app.route('/incorrect_login_creds', methods=['GET'])
def incorrect_login_creds():
    return render_template('credential-error.html')


# Verifying the email and password for the order dept login.
@app.route('/verify/<mail>/<password>')
def check_password(mail, password):
    if (mail == Order_Email and password == Order_Password):
        return redirect(url_for('auth_po_contents'))
    else:
        print ("Sorry, but you entered the incorrect password!!!")
        return redirect(url_for('incorrect_login_creds'))

# Login Page, enter email and password
@app.route("/", methods=['POST', 'GET'])
def home():
    print ("enter")
    if request.method == 'POST':
        email_order = request.form['EmailID']
        pass_order = request.form['Password']
        return redirect(url_for('check_password', mail = email_order, password = pass_order))
    return render_template('login.html')

if __name__ == '__main__':
     app.run()
