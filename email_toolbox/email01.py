import os
from datetime import datetime
import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def main(aPicTaker, aMsg):
	print("Starting to Send Email")
	#Define time stamp & record an image
	pic_time = datetime.now().strftime('%Y%m%d%H%M%S')
	#command = 'raspistill -w 1280 -h 720 -vf -hf -o '+pic_time+'.jpg'
	#os.system(command)
	print("About to save Image")
	aPicTaker.saveIm(pic_time+'.jpg')
	print("Image Saved")
	#Email information
	smtpUser = "cyhap.rpi@gmail.com" # ADD EMAIL ADDRESS
	smtpPass = #ADD PASSWORD

	#Destination Email Information

	toAdd = 'ENPM809TS19@gmail.com'
	fromAdd = smtpUser
	subject = 'Image Recorded at: ' + pic_time
	print("About to hit and multipart")
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = fromAdd
	msg['To'] = toAdd
	msg.preable = subject

	#Email Text
	body = MIMEText(aMsg)
	msg.attach(body)

	#Atach image
	fp = open(pic_time + '.jpg','rb')
	img = MIMEImage(fp.read())
	fp.close()
	msg.attach(img)
	
	# Send email
	print("About to send email")
	s = smtplib.SMTP('smtp.gmail.com', 587)
	print("Before ehlo")
	s.ehlo()
	print("before startttls")
	s.starttls()
	print("before 2nd ehlo")
	s.ehlo()

	print("Before Login")
	s.login(smtpUser, smtpPass)
	print("Before SendMail")
	s.sendmail(fromAdd, toAdd, msg.as_string())
	print("Before Quit")
	s.quit()

	print("Email delivered!")

