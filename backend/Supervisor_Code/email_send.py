from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from user_email_info import *
import smtplib

def email_sender(dest_address):
    # Setting up to, from subject, and body of email to be sent.
    message = MIMEMultipart()
    message['From'] = super_gmail
    message['To'] = dest_address
    message['Subject'] = 'Secure Email'
    email_body = 'Encrypted email sent from the SUPERVISOR' 
    message.attach(MIMEText(email_body, 'plain')) # Attach the text as plaintext to the email being sent.

    purchaseorder_sup = 'purchaseorder_sup.txt' # Setting the file name to be read.
    email_attachment = open('pathto_purchasorder_sup.txt', 'rb') # Open the purchaseorder.txt file as binary mode.

    multipart_base = MIMEBase('application', 'octet-stream') # Sets email attachment type as a binary file (like .exe, or .doc)
    multipart_base.set_payload(email_attachment.read()) # Set the payload of the message.
    encoders.encode_base64(multipart_base) # Encode the contents to base64.
    multipart_base.add_header('Content-Disposition', 'attachment; filename = %s' % purchaseorder_sup) # Set addition params for the email header field for the attachements.
    message.attach(multipart_base) # Attach the attachment to the email.

    # Email sending functionality.
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as email_server: # 25, 465, or 587
            email_server.starttls() # Start a secure connection if one not already established.
            email_server.login(super_gmail, super_pass) # Login to the email server as the supervisor.
            message_flat_string = message.as_string() # Return the message as a flattend string.
            email_server.sendmail(super_gmail, dest_address, message_flat_string) # Send the email from the supervisor to the provided destination address.
            email_server.quit() # Close the connection of the email server.
    except Exception as e:
        print(e)