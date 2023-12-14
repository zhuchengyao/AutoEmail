import time
import get_api
import os
import openai
from openai import OpenAI
import imaplib
import email
import mail_api
import smtplib
import ssl
from email.message import EmailMessage

Email_Address = '23262010051@m.fudan.edu.cn'
Password = mail_api.en_wechat_api


def message_append(message_queue, content, role="assistant"):
    if role == "assistant":
        append_mes = {
            "role": "assistant",
            "content": content
        }
    else:
        append_mes = {
            "role": "user",
            "content": content
        }
    message_queue.append(append_mes)
    return message_queue


def send_email(to_whom, content, sender=Email_Address):
    msg = EmailMessage()
    msg['Subject'] = 'Yao reply'
    msg['From'] = sender
    msg['To'] = to_whom
    msg.set_content(content)
    smtp.send_message(msg)


def read_unseen_email(Email_Address=Email_Address, Password=Password):
    server = imaplib.IMAP4_SSL(host='imap.exmail.qq.com', port=993)
    server.login(Email_Address, Password)
    server.select("Inbox")
    typ, data = server.search(None, "UNSEEN")  # 这个步骤获得没有阅读过的邮件
    # 标记为已读
    num_store = data[0].split()
    if not num_store:
        return 0
    else:
        server.store(num_store[0], '+FLAGS', '\\Seen')
    # 解码
    decode_num = data[0].decode('utf-8')
    unsee_title = decode_num.split()
    num_unsee = len(unsee_title)
    if(num_unsee==0):
        return 0
    fetch_data_lst = []

    for num in data[0].split():  # data[0].split()选择没有阅读过的邮件的ID,放入num
        typ, fetch_data = server.fetch(num, 'RFC822')
        fetch_data_lst.append(fetch_data)
        msg = email.message_from_bytes(fetch_data_lst[0][0][1])

    msg_list = []
    to_GPT_Message = ''
    for i in range(num_unsee):
        msg = email.message_from_bytes(fetch_data_lst[i][0][1])
        msg_list.append(msg)
        print(msg['from'])

    for msg in msg_list:
        content = 'from: ' + msg['from'] + '. \n' + 'message: '

        for part in msg.walk():
            a = part.get_content_maintype()
            if part.get_content_maintype() == 'text':
                body = part.get_payload(decode=True)
                text = body.decode('utf8')

                content = content + text + '\n'
            else:
                context = content + 'no message' +'\n'
            to_GPT_Message = to_GPT_Message + content
    return to_GPT_Message

# 发件人邮箱账号

# user登录邮箱的用户名，password登录邮箱的密码（授权码，即客户端密码，非网页版登录密码），但用腾讯邮箱的登录密码也能登录成功
Email_PassWord = mail_api.en_wechat_api
server = imaplib.IMAP4_SSL(host='imap.exmail.qq.com', port=993)
server.login(Email_Address, Password)
smtp = smtplib.SMTP_SSL(host='smtp.exmail.qq.com', port=465)
smtp.login(Email_Address, Email_PassWord)









ChatAPI=get_api.get_openai_api()

gpt_model="gpt-3.5-turbo"
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get(ChatAPI),
)



message = ("hello, this is Yao, You are going to be my email assistant. I will give my unread email in format of :"
           "'from:  content:' help me generate important information and tell me. If I want you help me reply the email"
           "then format the output like this: '$|target_email_address|content'. I will tell you who you gonna reply and "
           "the content. For example, if pchiang@fudan.edu.cn send me an email and I tell you reply to him 'I will be "
           "there, then you give me '$|pichiang@fudan.edu.cn|I will be there'. if you understand me, say yes" )
message_queue = []
message_queue = message_append(message_queue, message, "user")

num_detected_objs = 0


response = openai.chat.completions.create(
    messages=message_queue,
    model=gpt_model,
)
message_queue = message_append(message_queue, response.choices[0].message.content)
now_mes = response.choices[0].message.content
print(now_mes)

while True:
    unread_message = read_unseen_email()
    while unread_message == 0:
        time.sleep(600)
        unread_message = read_unseen_email()
    # now_mes = "$|czhu@aum.edu|I will be there"
    message_queue = message_append(message_queue, unread_message, "user")
    response = openai.chat.completions.create(
        messages=message_queue,
        model=gpt_model,
    )
    now_mes = response.choices[0].message.content
    print(now_mes)
    content_mes = input()
    message_queue = message_append(message_queue, content_mes, "user")
    response = openai.chat.completions.create(
        messages=message_queue,
        model=gpt_model,
    )
    now_mes = response.choices[0].message.content
    # print(now_mes)

    if (now_mes[0] == '$'):
        list_info = now_mes.split('|')
        print(list_info)
        sending_content = f"Subject: AI assistant reply\n\n{list_info[2]}"
        send_email(list_info[1], list_info[2])
    else:
        pass









