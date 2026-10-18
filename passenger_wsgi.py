import sys
import os

# Mevcut dizini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# cPanel / Phusion Passenger için WSGI application nesnesi
from app import app as application

if __name__ == '__main__':
    application.run()
