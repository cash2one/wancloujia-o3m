# coding: utf-8
import redis
import logging
import logging.config
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import FileSystemLoader, Environment, Template
from django.core.mail import EmailMultiAlternatives

from suning import settings

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("email_service")


env = Environment(loader=FileSystemLoader('templates'))
t = env.get_template(u'notify.html')
r = redis.StrictRedis()

def _send_email(subject, content, to):
	msg=MIMEMultipart('alternative')
	msg['subject']=subject
	msg['from']=settings.FROM_EMAIL
	msg['to']=';'.join((to,))
	part=MIMEText(content, 'html', 'utf-8')
	msg.attach(part)

	smtp=smtplib.SMTP()
	smtp.connect('smtp.qq.com')
	smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
	smtp.sendmail(settings.FROM_EMAIL, to, msg.as_string())
	smtp.quit()


def main():
	while True:
		item = r.blpop("users")
		user = json.loads(item[1])
		logger.debug(str(user))
		
		content = t.render(username=user["username"], realname=user["realname"], 
							password=user["password"], link=user["link"])
		subject = u'乐语豌豆荚手机助手后台账号已经开通'
		try:
			_send_email(subject, content, user["email"])
			logger.debug("email has been sent")
		except Exception as e:
			logger.exception(e)

if __name__ == "__main__":
	main()	
