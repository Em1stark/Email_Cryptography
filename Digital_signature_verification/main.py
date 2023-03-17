import imaplib
import email
import os
import hashlib
import rsa

# Данные: nanovipbnl@gmail.com eoydxrbgojorhznc
# Ввод данных для подключения к почтовому сервису и получения писем
imap_server = 'imap.gmail.com'
imap_port = 993
username = input("Имя пользователя (адрес электронной почты): ")
password = input("Пароль: ")

# Подключение к почтовому сервису
with imaplib.IMAP4_SSL(imap_server, imap_port) as mail:
    mail.login(username, password)
    mail.select('inbox')
    _, search_data = mail.search(None, 'ALL')
    mail_ids = search_data[0].split()

    # Получение последнего письма
    latest_mail_id = mail_ids[-1]
    _, msg_data = mail.fetch(latest_mail_id, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])

            # Извлечение текста письма и хеша
            message_text = ""
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    message_text = part.get_payload()
                    break
            hash = hashlib.sha256(message_text.encode('utf-8')).digest()
            print(hash)
            # Получение открытого ключа отправителя из файла public_key.pem
            for attachment in msg.get_payload():
                if attachment.get_filename() == 'public_key.pem':
                    public_key_data = attachment.get_payload(decode=True)
                    pubkey = rsa.PublicKey.load_pkcs1(public_key_data)

            # Получение ЭЦП из файла signature.pem
            for attachment in msg.get_payload():
                if attachment.get_filename() == 'signature.pem':
                    signature_data = attachment.get_payload(decode=True)
                    signature = signature_data

            # Проверка подписи сообщения с использованием открытого ключа отправителя
            try:
                rsa.verify(hash, signature, pubkey)
                print("Подпись действительна!")
            except:
                print("Подпись не действительна!")
