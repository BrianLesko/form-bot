# Brian Lesko 
# Scrape emails and parse for different form types. 

from email_retriever import EmailRetriever
from mysecrets import EMAIL, PASSWORD, EMAIL2, PASSWORD2

class BasicEmailObject:
    def __init__(self, email):
        self.email = email
        self.from_ = email['From']
        self.to = email['To']
        self.subject = email['Subject']
        self.type = self.categorize_email(email['Subject'])

    def categorize_email(self, subject):
        subject = subject.lower()
        if subject == "vacation request":
            return "timeoff request"
        elif "vacation approved" in subject:
            return "timeoff approval"
        elif "vacation not approved" in subject:
            return "timeoff denial"
        elif "audit request" in subject:
            return "audit request"
        elif "job application" in subject:
            return "job application"
        elif "feedback" in subject:
            return "employee feedback"
        else:
            return "other"

my_timeoff_email = EmailRetriever(EMAIL, PASSWORD)
my_form_email = EmailRetriever(EMAIL2, PASSWORD2)

# fetch the last 24 hours of emails
n_days = 1
new_timeoff_mail = my_timeoff_email.update_json_records(n_days_to_fetch=n_days)
new_form_mail = my_form_email.update_json_records(n_days_to_fetch=n_days)

emails = new_timeoff_mail + new_form_mail

# create a list of BasicEmailObject instances
email_objects = [BasicEmailObject(email) for email in emails]

# count the number of each form type
timeoff_requests = [email for email in email_objects if email.type == "timeoff request"]
timeoff_approvals = [email for email in email_objects if email.type == "timeoff approval"]
timeoff_denials = [email for email in email_objects if email.type == "timeoff denial"]
audit_requests = [email for email in email_objects if email.type == "audit request"]
job_applications = [email for email in email_objects if email.type == "job application"]
employee_feedback = [email for email in email_objects if email.type == "employee feedback"]

# print the number of each
print(f"Total emails: {len(email_objects)}")
print(f"Timeoff requests: {len(timeoff_requests)}")
print(f"Timeoff approvals: {len(timeoff_approvals)}")
print(f"Timeoff denials: {len(timeoff_denials)}")
print(f"Audit requests: {len(audit_requests)}")
print(f"Job applications: {len(job_applications)}")
print(f"Employee feedback: {len(employee_feedback)}")

email_summary = "\n".join([
    f"In the last 24 hours:",
    f"Vacation has been requested by: {[request.to for request in timeoff_requests]}.",
    f"Time off has been approved for: {[approval.to for approval in timeoff_approvals]}.",
    f"Time off has been denied for: {[denial.to for denial in timeoff_denials]}.",
    f"{len(audit_requests)} Audits have been requested.",
    f"{len(job_applications)} Job applications have been submitted.",
    f"{len(employee_feedback)} Employee feedback emails have been received."
    f"To view the PTO calendar, including requests and denials: cleanmybuilding.co/timeoff/calendar/"
    f"To view the job applications, audit requests, and employee feedback, please check the info@crystalclearBuildingServices.com or ContactUs@cleanmybuilding.co"
]).replace("\n", "<br>")


from simpleEmailSender import SimpleEmailSender
SimpleEmailSender("Email Summary", email_summary, 'smlesko@ccbs1.com').send_email()
SimpleEmailSender("Email Summary", email_summary, 'dan@ccbs1.com').send_email()
SimpleEmailSender("Email Summary", email_summary, 'joe@ccbs1.com').send_email()
print("Emails sent!")

