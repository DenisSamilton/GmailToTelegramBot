import sys
import imaplib
import email
import email.header
import datetime
import quopri


EMAIL_ACCOUNT = "tef.tr62@gmail.com"


def process_mailbox(imapmail):
    result, data = imapmail.search(None, '(FROM "lis.kostiantyn@gmail.com" SUBJECT "Home assignment")')
    if result != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        result, data = imapmail.fetch(num, '(RFC822)')
        if result != 'OK':
            print("\n\nERROR: getting message\n\n", num)
            continue

        try:
            msg = email.message_from_bytes(data[0][1])
        except Exception as e:
            print("\n\nERROR: making message\n\n")
            continue

        try:
            hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
            subject = str(hdr)
        except Exception as e:
            print("\n\nWARNING: making header\n")
            subject = "nil"

        print('Message %s: %s' % (num, subject))
        print('Raw Date:', msg['Date'])

        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            print("Local Date:", local_date.strftime("%a, %d %b %Y %H:%M:%S"))

        if msg.is_multipart():
            body = ""
            for payload in msg.get_payload():
                body += payload.get_payload()
        else:
            body = msg.get_payload()

        body = quopri.decodestring(body)
        body = body.decode('windows-1251')

        if body.startswith("Здравствуйте, ."):
            body = body.partition("Здравствуйте, .")
            body = body[2].strip()
        else:
            body = body.strip()

        if body.endswith("mailto:lis.kostiantyn@gmail.com"):
            body = body.partition("--")
            body = body[0].strip()
        else:
            body = body.strip()

        if body.find("All the materials are here") != -1:
            body = body.partition("All the materials are here")
            body = body[0].strip() + '\n\n' + body[1] + body[2]

        print("Body:\n" + body + '\n')


mail = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    print("Enter password: ")
    result, data = mail.login(EMAIL_ACCOUNT, sys.stdin.readline().rstrip())
except imaplib.IMAP4.error:
    print("LOGIN FAILED!!! ")
    sys.exit(1)

print(result, data)

mail.list()
mail.select("INBOX")

print("Processing mailbox...\n")
process_mailbox(mail)

mail.close()
mail.logout()