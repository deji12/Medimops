# Define the path to your chromedriver
from selenium.webdriver.chrome.service import Service

CHROME_DRIVER_SERVICE = Service('Bot/chromedriver.exe')

GOLOGIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NmViMGUzM2I1NmQ1NzBlMDc4MmJhOGYiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NmViMTRlNmQyNjkxMDEwNGViMDA3NGUifQ.Go4oW77gWn8G6fQ3IlCtoSBHlYg9r3HNlcAKQugn0qI"
PROFILE_ID = "66eb35b3bf4f526b70788d60"
PROFILE_PATH = r' C:\Users\Admin\Desktop\projects\medimops\medimops-backend\MedimopsBackend\Bot'

# AUTHENTICATION
EMAIL = "ptutsi@proton.me"
PASSWORD = "Mwr_c,4zP5TmAGb"

# CART 
MAX_PRODUCT_INCREMENTS = 10

# PAYMENT CARD DETAILS
CARD_TYPE = "Visa"
CARD_NUMBER = "4519460039959178"
CARD_HOLDER_NAME = "AYODEJI ADESOLA"
VALID_UNTIL_MONTH = 9
VALID_UNTIL_YEAR = 2027
CVV = 426

# COLOR FORMATS
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'