import email
import imaplib




class GmailClient:
	# Mail Client
	mail_client = None
	# User Config
	user_email = ""
	# Config
	google_imap_server = "imap.gmail.com"
	gmail_spam_folder = "[Gmail]/Spam"
	
	gmail_trash_folder = "[Gmail]/Trash"

	def __init__(self):
		self.mail_client = imaplib.IMAP4_SSL(self.google_imap_server)

	def __xoauth_authenticate(self, email, token):
		access_token = token['access_token']
		def _auth(*args, **kwargs):
			return 'user=%s\1auth=Bearer %s\1\1' % (email, access_token)
		return 'XOAUTH2', _auth

	def login_mail_client(self, email, token):
		try:
			self.mail_client.authenticate(*self.__xoauth_authenticate(email, token))
			return True
		except Exception as e:
			print("Error Occured! Please Retry...")
			return False

	def fetch_mails(self, mail_folder="INBOX"):
		return self.mail_client.select(mail_folder)

	def clean_spam(self, mail_folder="[Gmail]/Trash", commit_changes=True):
		"""
			Cleans the "[GMail]/Trash folder clean"
		"""
		print("Cleaning...")
		self.mail_client.select(mail_folder)
		print("Cleaning " + mail_folder + " folder...")
		typ, data = self.mail_client.search(None, "ALL")
		for num in data[0].split():
			self.mail_client.store(num, "+FLAGS", r'(\Deleted)')
		if commit_changes:
			self.mail_client.expunge()
		else:
			print("Emails were not deleted. Proceed to commit changes when needed...")
		return

	def commit_changes(self):
		self.mail_client.expunge()

	def logout(self):
		self.mail_client.close()
		self.mail_client.logout()

