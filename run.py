import os
import webbrowser
import schedule
from login import GoogleLogin
import time
import base64
import json
import dill as pickle


import threading


from mailcleaner import GmailClient





# configs
client_id = None
client_secret = None
clean_interval = 360 # 6 Min

# user
auth_client = None
gmail_client = None
user_email = None
user_token = None

# from file
google_client_config = "google_config.json"
login_credentials_file = "login_credential.json"




def load_credentials():
	# try:
	login_creds = open(login_credentials_file, 'r').read()
	login_creds = json.loads(login_creds)
	global user_email
	global user_token
	global client_id
	global client_secret
	global auth_client
	global clean_interval
	user_email = login_creds["user_email"]
	user_token = pickle.loads(base64.b64decode(login_creds["user_token"]))
	auth_client = pickle.loads(base64.b64decode(login_creds["auth_client"]))
	client_id = (base64.b64decode(login_creds["client_id"])).decode()
	client_secret = (base64.b64decode(login_creds["client_secret"])).decode()
	clean_interval = login_creds["clean_interval"]
	print("[+] Credentials Loaded for email: " + user_email)
	return True
	# except:
	# 	return False


def login_with_google():
	# If Config file is present use the config file
	global auth_client, client_id, client_secret, user_token
	# Create and login
	try:
		if os.path.exists(google_client_config):
			gauth = GoogleLogin(client_id, client_secret)
			gauth.load_from_file(google_client_config)
		else:
			print("Google OAuth Client Config file was not found.")
			print("Please ensure that \'" + google_client_config + "\' file exists in the present directory\n")
			print("To Obtain your client_id and client_secret go to: https://console.cloud.google.com/apis/credentials\n")
			while not client_id:
				print("[MANUAL INPUT]")
				client_id = input("> Please Enter Google Oauth Client ID: ")
			while not client_secret:
				print("[MANUAL INPUT]")
				client_secret = input("> Please Enter Google Oauth Client Secret: ")
			gauth = GoogleLogin(client_id, client_secret)
		# Get a Auth URL
		auth_url = gauth.create_auth_url()
		# Start Localhost bottle server
		#
		# Spawn Browser
		webbrowser.open(auth_url)
		try:
			os.system("termux-open-url " + auth_url)
		except:
			pass
		# Print Instructions
		print("[!]\tPlease Login with your google account and give email access.")
		print("\tThis is a one time login and wouldnt be required after logging in.\n")
		print("[Note]: If ater login you get a blank page starting with 'localhost' please copy the url and paste below.\n\n")
		auth_url = input("> Enter url here after being redirected: ")
		while auth_url==None:
			auth_url = input("> Enter url here: ")
		# Prevent HTTPS Issues
		if "http:" in auth_url:
			auth_url = auth_url.replace("http:", "https:")
		# Try get token
		user_token = gauth.create_token(auth_url)
		if not user_token:
			print("[!] Error Occured in Logging in. Please run the script again.")
			wait_and_exit()
		# Store the gauth
		auth_client = gauth
		client_id = auth_client.client_id
		client_secret = auth_client.client_secret
		return user_token
		print("[!] Unknown Error Occured...")
		wait_and_exit()
	except:
		wait_and_exit()


def setup_email_client():
	"""
		Setup
	"""
	global auth_client
	global user_email
	if not user_email:
		user_email = auth_client.get_user_email()
	if not user_email:
			print("[!] There was an error in obtaining user email.")
			user_email = input("> Please manually enter your account email here: ")
	global gmail_client
	gmail_client = GmailClient()
	if not gmail_client.login_mail_client(user_email, user_token):
		print("[!] There was an error logging in to imap servers. please try again")
		wait_and_exit()
	return True


def save_credentials():
	"""
		Save Login credentials for later use
	"""
	try:
		global client_id, client_secret, user_email, user_token, auth_client, clean_interval
		user_token_pickle = (base64.b64encode(pickle.dumps(user_token,0))).decode()
		auth_client_pickle = (base64.b64encode(pickle.dumps(auth_client,0))).decode()
		credentials = { "client_id" : base64.b64encode(client_id.encode()).decode(), "client_secret" : base64.b64encode(client_secret.encode()).decode(), "clean_interval" : clean_interval, "user_email": user_email, "user_token" : str(user_token_pickle), "auth_client" : str(auth_client_pickle) }
		credentials = json.dumps(credentials,indent=4)
		with open(login_credentials_file, 'w') as file:
			file.write(credentials)
			file.close()
	except:
		print("There was an error in saving the credentials to a file")
	return True


def clean_spam():
	"""
		clean spam
	"""
		#
	global gmail_client
	print("Cleaning now...")
	gmail_client.clean_spam("[Gmail]/Trash")
	gmail_client.clean_spam("[Gmail]/Spam")
		


def clean_in_background():
	# run
	global clean_interval
	schedule.every(clean_interval).seconds.do(clean_spam)
	while True:
		schedule.run_pending()
		time.sleep(1)

def main():
	"""
		Main Method
	"""
	global gmail_client
	global auth_client
	global user_token
	if os.path.exists(login_credentials_file):
		print("[+] Login Credentials Found...")
		load_credentials()
	if not user_token and not auth_client:
		login_with_google()
	if not gmail_client:
		print("[+] Creating New GmailClient...")
		setup_email_client()
	if gmail_client:
		save_credentials()
	print("[+] Spam Cleaning will now be done in background...")
	threading.Thread(target=clean_in_background,args=()).start()
	# 

def wait_and_exit():
	"""
		Wait then exit
	"""
	input("\n[Press any key to exit...]")
	exit()


if __name__ == '__main__':
	main()
