import logging

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.utils.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, DOMAIN_NAME, MAIL_STARTTLS, \
    MAIL_SSL_TLS, VALIDATE_CERTS, RESET_PASS_URL

logger = logging.getLogger(__name__)

mail_conf = ConnectionConfig(
    MAIL_USERNAME=SMTP_USERNAME,
    MAIL_PASSWORD=SMTP_PASSWORD,
    MAIL_FROM=SMTP_USERNAME,
    MAIL_PORT=SMTP_PORT,
    MAIL_SERVER=SMTP_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=VALIDATE_CERTS,
)


async def send_new_pass(email: str, token: str) -> bool:
    try:
        html_content = f"""
    <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Сброс пароля</title>
<style>
    body {{
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 0;
    }}
    .container {{
        max-width: 600px;
        margin: 20px auto;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}
    h1 {{
        color: #333;
        text-align: center;
        margin-bottom: 20px;
    }}
    p {{
        color: #666;
        text-align: center;
        margin: 10px 0;
    }}
    .btn {{
        display: inline-block;
        padding: 15px 25px;
        margin: 20px 0;
        background-color: #4CAF50;
        font-size: 18px;
        border-radius: 5px;
        text-decoration: none;
        color: white;
        font-weight: bold;
    }}
    .footer {{
        text-align: center;
        color: #999;
        font-size: 12px;
        margin-top: 20px;
    }}
</style>
</head>
<body>
<div class="container">
    <h1>Сброс пароля</h1>
    <p>Вы получили это письмо, потому что вы или кто-то другой запросили сброс пароля для вашего аккаунта.</p>
    <p>Нажмите на кнопку ниже, чтобы изменить пароль:</p>
    <center>
        <a href="https://{DOMAIN_NAME}/{RESET_PASS_URL}{token}" class="btn">Изменить пароль</a>
    </center>
    <p>Если вы не запрашивали сброс пароля или считаете, что это ошибка, пожалуйста, проигнорируйте это сообщение.</p>
    <div class="footer">
        <p>С уважением, команда поддержки.</p>
    </div>
</div>
</body>
</html>
    """
        message = MessageSchema(
            subject="Сброс пароля",
            recipients=[email],
            body=html_content,
            subtype="html",
            charset="utf-8"
        )

        fm = FastMail(mail_conf)
        await fm.send_message(message)

        logger.info(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки письма: {e}")
        return False
