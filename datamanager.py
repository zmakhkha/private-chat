import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
conn = sqlite3.connect(BASE_DIR / 'db2.sqlite3')

# Build paths inside the project like this: BASE_DIR / 'subdir'.

print ("Opened database successfully")
