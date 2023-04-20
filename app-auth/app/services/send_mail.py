import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

# 邮件服务器信息
smtp_server = 'smtp.163.com'
smtp_port = 465
smtp_username = '18860279853@163.com'
smtp_password = 'UPWRPLVJLEXAEIYQ'


def send_mail(to_mail, register_key):
    # 发件人和收件人信息
    from_email = '18860279853@163.com'
    to_emails = [to_mail]

    # 构造邮件
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ','.join(to_emails)
    msg['Subject'] = 'Test email from Python'

    # 邮件正文
    body = f"""
    <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>激活账号</title>
        </head>
        <body>
            <h2>欢迎hf-phish网站！</h2>
            <p>请点击以下链接激活您的账号：</p>
            <p><a href="{{ activation_link }}">{register_key}</a></p>
            <p>如果您没有注册，请忽略此邮件。</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # # 添加附件
    # with open('/path/to/attachment.pdf', 'rb') as f:
    #     attachment = MIMEApplication(f.read(), _subtype='pdf')
    # attachment.add_header('Content-Disposition', 'attachment', filename='attachment.pdf')
    # msg.attach(attachment)

    # # 添加图片
    # with open('/path/to/image.png', 'rb') as f:
    #     image = MIMEImage(f.read())
    #     image.add_header('Content-ID', '<image1>')
    #     msg.attach(image)

    # 发送邮件
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_emails, msg.as_string())
