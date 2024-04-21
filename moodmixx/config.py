import base64
import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'
CLIENT_ID = '913923a1251d4f90b46aedfee11d2f6b'
CLIENT_SECRET = '10869cb3995f4e75afa8d8a12cc40106'
SCOPE = 'user-library-read user-library-modify playlist-modify-public playlist-modify-private'
AUTHORIZATION = f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}"
