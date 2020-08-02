import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError




class GoogleLogin:
	# Client Session
	authorization_url = None
	auth_client = None
	token = None
	# Config
	redirect_uri = "https://localhost:8008/auth"
	authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
	token_url = "https://oauth2.googleapis.com/token"
	refresh_url = token_url
	scope = [ "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid", "https://mail.google.com/" ]
	# info url
	user_info_uri = "https://www.googleapis.com/oauth2/v1/userinfo"
	# user data

	user_info = None

	def __init__(self, client_id, client_secret, redirect_uri=None, authorization_base_url=None, token_url=None, scope=None, refresh_url=None, token=None):
		"""
			Init the GoogleAuthClient
		"""
		self.client_id = client_id
		self.client_secret = client_secret
		# Check if parameter is provided
		# Set if parameter is provided
		if redirect_uri:
			self.redirect_uri = redirect_uri
		if authorization_base_url:
			self.authorization_base_url = authorization_base_url
		if token_url:
			self.token_url = token_url
		if scope:
			self.scope = scope
		if refresh_url != token_url:
			self.refresh_url = refresh_url
		if token:
			self.token = token
		# [ COMPLETE ]

	def load_from_file(self, file_name):
		"""
			Parse Google CLient Config.json
		"""
		try:
			config_file = open(file_name, 'r').read()

			config_file = json.loads(config_file)["installed"]
			self.client_id = config_file["client_id"]
			self.client_secret = config_file["client_secret"]
			self.authorization_base_url = config_file["auth_uri"]
			self.token_url = config_file["token_uri"]
			self.refresh_url = self.token_url
			self.redirect_uri = "http://localhost"
		except Exception as e:
			print("Error Occured when importing config file...")
			return False
		return True



	def create_auth_url(self, client_id=None):
		"""
			Returns Google Auth URL
		"""
		if client_id:
			self.client_id = client_id
		self.auth_client = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)
		authorization_url, state = self.auth_client.authorization_url(self.authorization_base_url, access_type="offline", prompt="select_account")
		return authorization_url


	def create_token(self, redirect_response,client_secret=None, token_url=None):
		"""
			Create email auth token
		"""
		if client_secret:
			self.client_secret = client_secret
		if token_url:
			self.token_url = token_url
		# 
		if not self.token:
			try:
				self.token = self.auth_client.fetch_token(self.token_url, client_secret=self.client_secret, authorization_response=redirect_response)
			except MismatchingStateError:
				print("The provided response uri does not coincide with the auth_uri.\nPlease login with new auth_uri.")
			except Exception as e:
				print(str(e))
				print("Error Occured in Fetching token. Please Login Again")
		return self.token


	def refresh_token(self, token=None, user_info_uri=None):
		"""
			Refresh Token
		"""
		# updated token is the previous token
		# in case the token expired, we refresh it
		if token:
			self.token = token
		if user_info_uri:
			self.user_info_uri = user_info_uri
		updated_token = self.token
		try:
			update_client = OAuth2Session(self.client_id, token=updated_token)
			auth_client.get(self.user_info_uri)
		except TokenExpiredError as e:
			try:
				updated_token = self.auth_client.refresh_token(self.refresh_url)
				self.token = updated_token
			except:
				print("Error Occured While refreshing token... Please Try Again.")
		# Return updated_token
		return updated_token


	def get_user_info(self):
		"""
			Returns userdata as json
		"""
		if not self.user_info:
			try:
				r = self.auth_client.get('https://www.googleapis.com/oauth2/v1/userinfo')
				self.user_info = r.json()
			except:
				print("Error Getting User info")
		return self.user_info



	def get_user_email(self):
		"""
			Returns user email
		"""
		user_email = None
		if not self.user_info:
			try:
				r = self.auth_client.get('https://www.googleapis.com/oauth2/v1/userinfo')
				self.user_info = r.json()
			except:
				print("Error Getting User info")
		# Return user email
		try:
			user_email = self.user_info['email']
			print("User Email Found: " + user_email)
		except:
			print("Unable to parse user info")
		return user_email