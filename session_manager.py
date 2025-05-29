import hrequests

# Create a shared session object
session = hrequests.Session()

def get_session():
    return session 