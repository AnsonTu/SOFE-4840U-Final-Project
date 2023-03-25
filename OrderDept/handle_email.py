import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
sys.path.insert(0, "/home/musselman/Downloads/SecProj/Database")
sys.path.insert(0, "/home/musselman/Downloads/SecProj")
import os
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
