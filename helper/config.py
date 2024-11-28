import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import subprocess
import shutil
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options

######################################## OpenAI ########################################
# Load environment variables
load_dotenv(override=True)

# Get OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

######################################## Exception ########################################
class LinkedInLoginError(Exception):
    """Custom exception for LinkedIn login failures"""
    pass

class InstagramLoginError(Exception):
    """Custom exception for Instagram login failures"""
    pass

class XLoginError(Exception):
    """Custom exception for Instagram login failures"""
    pass

class InvalidCredentialsError(InstagramLoginError):
    """Specific exception for invalid credentials"""
    pass

######################################## Logger ########################################
# Configure console-only logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

######################################## Get Current Path ########################################
try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'

######################################## Initialize Driver ########################################

def init_driver(load_images=True, is_headless=False):
    """
    Initialize the Chrome WebDriver using WebDriverManager for ChromeDriver handling.

    :param load_images: Boolean to enable or disable image loading in the browser.
    :param is_headless: Boolean to run the browser in headless mode.
    :return: Configured WebDriver instance.
    """
    # Configure Chrome options
    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    if not load_images:
        options.add_argument("--blink-settings=imagesEnabled=false")
    
    if is_headless:
        options.add_argument("--headless")

    # Set a custom user agent
    user_agent = 'Mozilla/5.0 (X11; ; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    options.add_argument(f"user-agent={user_agent}")
    options.binary_location='usr/bin/google-chrome'
    # Automatically manage ChromeDriver using WebDriverManager
    # driver = webdriver.Chrome(
    #     service=Service(
    #         ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
    #     ),
    #     options=options
    # )
    
    selenium_host = os.getenv('SELENIUM_HOST', 'localhost')
    selenium_port = os.getenv('SELENIUM_PORT', '4444')
    
    driver = webdriver.Remote(
        command_executor=f'http://{selenium_host}:{selenium_port}/wd/hub',
        options=options
    )
    return driver