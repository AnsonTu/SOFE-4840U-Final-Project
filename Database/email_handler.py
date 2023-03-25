import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import sys
sys.path.insert(0, r'/home/musselman/Downloads/SecProj/Database')
from email.mime.multipart import MIMEMultipart
from Credentials import *

# Function to create the email to be sent to the user, reflecting the status of their order request.
def send_confirmation_email(send_to_address, approval_status):
    # Creating the structure of the email.
    source_address = Order_Email
    email_structure = MIMEMultipart()
    email_structure['From'] = source_address
    email_structure['To'] = send_to_address
    email_structure['Subject'] = "SECURE MESSAGE: Your Order Approval Status"

    # Messages for either rejected or approved order requets.
    if(approval_status == "Approve"):
        email_body = "Good News! Your order was approved and confirmed."
    else:
        email_body = "Bad News. We regret to inform you that your requested order has not been approved. Please try again."

    # Sending the contents to a gmail account using port 587 (for TLS)
    email_structure.attach(MIMEText(email_body, 'plain'))
    email_server = smtplib.SMTP('smtp.gmail.com', 587)
    email_server.starttls()
    email_server.login(source_address, Order_Password)
    email_contents = email_structure.as_string()
    email_server.sendmail(source_address, send_to_address, email_contents)
    email_server.quit()

# Function that structures and sends a basic email with the encrypted PO to order and supervisors as an attachment.
def send_email_super_orderdept(dest_addr): 
    source_addr = Purchase_Email
 
    email_fields = MIMEMultipart()
 
    email_fields['From'] = source_addr
    email_fields['To'] = dest_addr
    email_fields['Subject'] = "Encrypted PO" 
 
    body = "Email was sent from the Purchase Dept [SECURE]"
 
    email_fields.attach(MIMEText(body, 'plain'))
 
    encrypt_file = "cust_PO.txt"
    attch = open("/home/musselman/Downloads/SecProj/purchase_center/cust_PO.txt", "rb")
 
    segment = MIMEBase('application', 'octet-stream')
    segment.set_payload((attch).read())
    encoders.encode_base64(segment)
    segment.add_header('Content-Disposition', "attachment; filename= %s" % encrypt_file)
 
    email_fields.attach(segment)
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_addr, Purchase_Password)
    email_text = email_fields.as_string()
    server.sendmail(source_addr, dest_addr, email_text)
    server.quit()

# Function to construct a basic email that is sent to the order dept from the supervisor containing the encrypted signed order.
def send_email_to_orderdept(dest_addr): 
    source_addr = Super_Email
 
    email_message = MIMEMultipart()
 
    email_message['From'] = source_addr
    email_message['To'] = dest_addr
    email_message['Subject'] = "Encrypted Order" 
 
    email_cont = "This email is from the Supervisor [SECURE]"
 
    email_message.attach(MIMEText(email_cont, 'plain'))
 
    attch_name = "super_PO.txt"
    attch = open("/home/musselman/Downloads/SecProj/Supervisor/super_PO.txt", "rb")
 
    segment = MIMEBase('application', 'octet-stream')
    segment.set_payload((attch).read())
    encoders.encode_base64(segment)
    segment.add_header('Content-Disposition', "attachment; filename= %s" % attch_name)
 
    email_message.attach(segment)
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_addr, Super_Password)
    email_text = email_message.as_string()
    server.sendmail(source_addr, dest_addr, email_text)
    server.quit()
