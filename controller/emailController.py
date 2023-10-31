import smtplib
def send_email(request):
    email_subject = request.form.get("email_subject")
    print(email_subject)
    email_body = request.form.get("email_body")
    email_to = request.form.get("email_to")

    gmail_user = 'jobrapid4@gmail.com'
    gmail_app_password = 'oukf vaum xwqs nofu'

    sent_from = gmail_user
    sent_to = [email_to]
    sent_subject = email_subject
    sent_body = (email_body)# Main Text

    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
