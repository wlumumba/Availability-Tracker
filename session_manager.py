import requests

# Create a shared session object
session = requests.Session()

def get_session():
    return session 