# -*- coding: utf8 -*
#04mar20kg
#python 3.7.1

import smtplib

def send_mail(mail_dict):
    HOST = "smtp.yandex.ru"
    SUBJECT = "test error " + ' ' + mail_dict["CONF"]
    TO = mail_dict["ADDR"]
    FROM = "error1cforever@yandex.ru"
    text = mail_dict["TEXT"]
    
    BODY = "\r\n".join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Subject: %s" % SUBJECT ,
        "",
        text
    ))
    BODY = BODY.encode("cp1251")
    server = smtplib.SMTP(HOST, 25, timeout=10)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(FROM, 'rjpfbdfyjdyf12345')
    server.sendmail(FROM, [TO], BODY)
    server.quit()
