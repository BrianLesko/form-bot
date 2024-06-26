# Brian Lesko
# 6/25/2024
# Pull email records from a google IMAP server, which allows 2.5 GB of pulls per day. This amounts to pulling over 100,000 emails if the emails are slim* 

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import json
import os

class EmailRetriever:

    def __init__(self,SENDER_EMAIL, SENDER_PASSWORD):
        self.email = SENDER_EMAIL
        self.password = SENDER_PASSWORD
        self.inbox = None
        self.sent = None
        self.mail = mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.login()
        self.n_days_to_fetch = 1

    def login(self):
        self.mail.login(self.email, self.password)

    def fetch_inbox(self):
        self.inbox = self.fetch_box('inbox')
        return self.inbox

    def fetch_sent(self):
        self.sent = self.fetch_box('"[Gmail]/Sent Mail"')
        return self.sent

    def decode_header(self, header_value):
        decoded_header = decode_header(header_value)
        header_parts = [str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else str(part[0]) for part in decoded_header]
        return ''.join(header_parts)

    def fetch_box(self, box):
        self.mail.select(box)
        date = (datetime.now() - timedelta(days=self.n_days_to_fetch)).strftime("%d-%b-%Y")
        # Use the 'SINCE' keyword to filter emails from the last 24 hours
        _, data = self.mail.uid('search', None, f"(SINCE {date})")
        email_ids = data[0].split()
        def fetch_email(e_id):
            _, email_data_raw = self.mail.uid('fetch', e_id, '(BODY.PEEK[])')
            raw_email = email_data_raw[0][1]
            email_message = email.message_from_bytes(raw_email)
            date_tuple = email.utils.parsedate_tz(email_message['Date'])
            date_str = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime("%a, %d %b %Y %H:%M:%S") if date_tuple else "Unknown"
            
            # Extract the content of the email
            if email_message.is_multipart():
                for part in email_message.get_payload():
                    if part.get_content_type() == 'text/plain':
                        content = part.get_payload()
            else:
                content = email_message.get_payload()
            
            return {
                "From": self.decode_header(email_message['From']),
                "To": self.decode_header(email_message['To']),
                "Subject": self.decode_header(email_message['Subject']),
                "Date": date_str,
                "Content": content  # Add the content to the returned dictionary
            }
        return [fetch_email(e_id) for e_id in email_ids]
    
    def write_to_json(self, inbox, sent, records=None):
        emails = inbox + sent + (records if records else [])
        emails_set = set(tuple(email.items()) for email in emails) # Convert list of dictionaries to set of tuples to remove duplicates
        emails = [dict(email) for email in emails_set] # Convert set of tuples back to list of dictionaries
        with open('emails.json', 'w') as f:
            json.dump(emails, f)
    
    def read_from_json(self,file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
        
    def update_json_records(self, n_days_to_fetch=1):
        self.n_days_to_fetch = n_days_to_fetch
        inbox = self.fetch_inbox()
        sent = self.fetch_sent()
        self.n_inbox = len(inbox)
        self.n_sent = len(sent)
        if os.path.isfile('emails.json'):
            # Write non duplicate emails to existing JSON
            try:
                records = self.read_from_json('emails.json') 
                self.write_to_json(inbox, sent, records) # writes to emails.json
            except:
                self.write_to_json(inbox, sent)
        else: # There exists no JSON file, make one
            self.write_to_json(inbox, sent)
        return inbox+sent # the new email records sent and received