import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

def init_driver(chrome_driver_dir='helper', load_images=True, is_headless=False):
    """
    Initialize the Chrome WebDriver with specified options.

    :param chrome_driver_dir: Path to the directory containing ChromeDriver binaries for different OSs.
    :param load_images: Boolean to enable or disable image loading in the browser.
    :param is_headless: Boolean to run the browser in headless mode.
    :return: Configured WebDriver instance.
    """
    # Detect the OS
    current_os = platform.system().lower()
    logger.info(f"Current OS detected: {current_os}")

    # Determine the appropriate ChromeDriver executable
    if current_os == "windows":
        chrome_driver = 'helper/driver/windows/chromedriver.exe'
    elif current_os == "linux":
        chrome_driver = 'helper/driver/linux/chromedriver'
    elif current_os == "darwin":  # macOS
        chrome_driver = 'helper/driver/macos/chromedriver'
    else:
        raise OSError(f"Unsupported operating system: {current_os}")

    logger.info(f"ChromeDriver path: {chrome_driver}")

    # Verify that the ChromeDriver file exists
    if not os.path.exists(chrome_driver):
        raise FileNotFoundError(f"ChromeDriver not found at {chrome_driver}")

    # Adjust driver permissions (Linux/macOS)
    if current_os in ["linux", "darwin"]:
        os.chmod(chrome_driver, 0o755)

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
    chrome_path = shutil.which("google-chrome")  # Linux/Mac
    logger.info(chrome_path)
    chrome_binary_path = "/usr/bin/google-chrome"  # Adjust this path based on your system
    options.binary_location = chrome_binary_path
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(executable_path=chrome_driver), options=options)
    logger.info(driver.capabilities['chrome']['binary'])

    logger.info("Chrome WebDriver initialized successfully")
    return driver