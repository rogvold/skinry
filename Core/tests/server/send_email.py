import smtplib
def mail(sender, subject, message, to):
   smtp_server = 'smtp.yandex.ru'
   smtp_port = 25
   smtp_pasword = 'password'
   mail_lib = smtplib.SMTP(smtp_server, smtp_port)
   mail_lib.login(sender, smtp_pasword)
   msg = 'From: %s\r\nTo: %s\r\nContent-Type: text/html; charset="utf-8"\r\nSubject: %s\r\n\r\n' % (sender, to, subject)
   msg += message
   mail_lib.sendmail(sender, to, msg)

message = "Hi Python!"
senderrs = ["almaz.nasibullin@gmail.com"]
mail("nasibyllin.almaz@yandex.ru", "Yeah Bitch! Magnets!", message, senderrs)