import MySQLdb
import pickle as pkl
import rsa
import hashlib
import os
import sys
from flask import Flask, redirect, url_for, render_template, request
from supervisor_handler import *
from werkzeug.utils import secure_filename
from email_send import *
from user_email_info import *

assets_folder = 'path_to_assets'
exetentions_utilized = set(['png', 'txt', 'pdf', 'jpg']) # Add more when needed.

length_of_gen_key = 1024
identifying_email = ''
password = ''
purchaseorder_supervisor = ''
purchaseorder = ''

# Setting up flask application.
flaskApp = Flask(__name__)
flaskApp.config['assets_folder'] = assets_folder

# Function to get the signature along with the message.
def signed_message_fetch():
    with open('purchaseorder.txt', 'r') as sitefiles:
        # Read the data within the purchaseorder.txt file
        purchase_data = sitefiles.read()
    # CHANGE THIS LINE BELOW!
    split_data = purchase_data.split('SSSS') # Split data based on the SSSS.
    user_pr_key = pr_retrieval(super_gmail) # Getting the private key of the supervisor.
    msg = rsa.decrypt(split_data[0], user_pr_key) # Decrypt message using the private key.
    msg = msg.decode('utf-8') # Decode the message to utf-8 mode.
    first_signature = rsa.decrypt(split_data[1], user_pr_key) # Get the first part of the signature by decrypting the 2nd part of the split data.
    second_signature = rsa.decrypt(split_data[2], user_pr_key) # Get the second part of the signature by decrypting the 3rd part of the split data.
    final_signature = first_signature + second_signature # Combine the keys to get the 'final key'
    content_writer = open('purchasorder_sup.txt', 'w') # Setup the file to write to.
    content_writer.write(msg) # Write the decrypted and decoded message.
    content_writer.close() # Close the writer.
    
    return (msg, final_signature)

# Function to write to the encrypted message.
def write_encrypted_msg(encrypted_msg):
    e_msg = open('purchaseorder_sup.txt', 'w')
    e_msg.write(encrypted_msg)
    e_msg.close()

# Function to get the email that is within the purchase order.
def email_fetch(email_data):
    extr_first = email_data.split('Email:')
    second_extr = extr_first[1].split('\n')
    
    return (second_extr[0])

# Encrypted attachment data.
def email_attach_fecth(message, pr_key, pu_key):
    global length_of_gen_key
    # Hash using MD5
    final_signature = rsa.sign(message, pr_key, 'MD5')
    convert_bytes = 1024 / 8
    # Encrypt the different sections of the message.
    rsa_encrypt = rsa.encrypt(message.encode('utf-8'), pu_key) + 'SSSS' + rsa.encrypt(final_signature[0:convert_bytes - 11], pu_key) + 'SSSS' + rsa.encrypt(final_signature[convert_bytes - 11], pu_key)

    return rsa_encrypt

# NEED TO CHANGE BELOW!

def purchaseorder_processing():
    global length_of_gen_key
    user_pr_key = pu_retrieval(identifying_email)           #get the private key of the user for signature 
    order_dept_pu = pu_retrieval(orderdept_gmail)
    with open('purchasorder_sup.txt', 'r') as sitefiles:	
        message = sitefiles.read()    #read the data from the file
    order_dept_encrypted = email_attach_fecth(message,user_pr_key,order_dept_pu)     #crypted data for  attachment of mail to order department
    write_encrypted_msg(order_dept_encrypted)      #create file for attachment of mail to order department
    email_sender(orderdept_gmail)        # send mail to order department
    os.remove("purchasorder_sup.txt")

@flaskApp.route('/approved', methods=['POST','GET'])
def approved():
    return render_template('approved.html')

@flaskApp.route('/display_po',methods=['POST','GET'])
def display_po(): 
    global PO
    if request.method == 'POST':
        if(request.form['Verify & Sign'] == 'Verify & Sign'):
            purchaseorder_processing()
        return render_template('approved.html')
    return render_template('display_po.html')

#display contents of purchase order
@flaskApp.route('/confirm_order',methods=['POST','GET'])
def confirm_order():
    if request.method == 'POST':
        if (request.form['Yes']=='Yes'):
            message,signature = signed_message_fetch() 
            user_email = email_fetch(message)
            public = pu_retrieval(user_email)
            if(rsa.verify(message, signature, public)):
            # do when signature and message match
                print ("Signature verified")
            return render_template('display_po.html', message_html = message)
    return render_template('confirm_order.html')

#upload the dowloaded encrypted file
@flaskApp.route('/authenticate_po', methods=['POST','GET'])
def authenticate_po():
    print ("Within uploaded file!'")
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(flaskApp.config['UPLOAD_FOLDER'], filename)) #save the file in path defined in UPLOAD_FOLDER
            return redirect(url_for('confirm_order'))
    return render_template('authenticate_po.html')

#displays error messgae for wrong credentials   
@flaskApp.route('/wrong_credentials', methods=['GET'])
def wrong_credentials():
    return render_template('wrong_credentials.html')

#email and pwd verification
@flaskApp.route('/verify')
def verify_pw():
    global identifying_email, password
    if (identifying_email == 'supervisorsecproj@gmail.com' and password == "supersecproj123"):
        return redirect(url_for('authenticate_po'))
    else:
        return redirect(url_for('wrong_credentials'))    

#Login Page, enter email and password
@flaskApp.route("/",methods=['POST','GET'])
def home():
    global identifying_email,password
    print ("enter")
    if request.method == 'POST':
        identifying_email = request.form['E_ID']
        password = request.form['Password']
        print(identifying_email, " ", password)
        return redirect(url_for('verify_pw'))
    return render_template('login.html')        

if __name__ == '__main__':
    flaskApp.debug == True
    flaskApp.run()