import os
os.environ['STATIC'] = os.path.join(os.getcwd(), 'Requip', 'static')
os.environ['FILES'] = os.path.join(os.getcwd(), 'Requip', 'media')
from dotenv import load_dotenv
load_dotenv()
from Requip import app