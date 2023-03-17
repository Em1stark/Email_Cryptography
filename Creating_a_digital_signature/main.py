import smtplib
import os
import hashlib
import rsa
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Генерация пары ключей RSA
(pubkey, privkey) = rsa.newkeys(512)
# Пароль для osmakovaov@gmail.com ttkrgbiixrnuhkmh
# Ввод данных для подключения к почтовому сервису и отправки письма
smtp_server = 'smtp.gmail.com'
smtp_port = 587
username = input("Имя пользователя (адрес электронной почты): ")
password = input("Пароль: ")
sender_email = username
recipient_email = input("Email получателя: ")
subject = input("Тема письма: ")
body = input("Текст письма: ")

# Создание объекта MIMEMultipart
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = recipient_email
message['Subject'] = subject

# Хеширование письма вместе с открытым ключом
message_text = body
hash = hashlib.sha256(message_text.encode('utf-8')).digest()

print(hash)
# Создание цифровой подписи с помощью закрытого ключа
signature = rsa.sign(hash, privkey, 'SHA-256')

# Создание вложения с открытым ключом
with open('public_key.pem', mode='wb') as publicfile:
    publicfile.write(pubkey.save_pkcs1())

# Создание вложения с ЭЦП
with open('signature.pem', mode='wb') as signaturefile:
    signaturefile.write(signature)

# Добавление текста письма в объект MIMEMultipart
#message_text = "Privet"
message_text = MIMEText(message_text)
message.attach(message_text)

# Добавление вложения в объект MIMEMultipart
with open('public_key.pem', 'rb') as f:
    attachment = MIMEApplication(f.read(), _subtype='pem')
    attachment.add_header('Content-Disposition', 'attachment', filename='public_key.pem')
    message.attach(attachment)

with open('signature.pem', 'rb') as f:
    attachment = MIMEApplication(f.read(), _subtype='pem')
    attachment.add_header('Content-Disposition', 'attachment', filename='signature.pem')
    message.attach(attachment)

# Отправка письма получателю
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(username, password)
    message_text_bytes = message.as_bytes()
    server.sendmail(sender_email, recipient_email, message_text_bytes)
    print("Письмо отправлено!")