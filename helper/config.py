import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
import platform
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

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

def init_driver(gecko_driver_dir='helper', load_images=True, is_headless=False):
    """
    Initialize the Firefox WebDriver with specified options.
    
    :param gecko_driver_dir: Path to the directory containing GeckoDriver binaries for different OSs.
    :param load_images: Boolean to enable or disable image loading in the browser.
    :param is_headless: Boolean to run the browser in headless mode.
    :return: Configured WebDriver instance.
    """
    # Detect the OS
    current_os = platform.system().lower()
    logger.info(current_os)
    # Determine the appropriate GeckoDriver executable
    if current_os == "windows":
        gecko_driver = os.path.join(gecko_driver_dir, "driver","windows", "geckodriver.exe")
    elif current_os == "linux":
        gecko_driver = os.path.join(gecko_driver_dir, "driver","linux", "geckodriver")
    elif current_os == "darwin":  # macOS

        gecko_driver = 'helper/driver/macos/geckodriver'


    else:
        raise OSError(f"Unsupported operating system: {current_os}")
    logger.info("********************#############")

    # Verify that the GeckoDriver file exists
    if not os.path.exists(gecko_driver):
        raise FileNotFoundError(f"GeckoDriver not found at {gecko_driver}")

    # Adjust driver permissions (Linux/macOS)
    if current_os in ["linux", "darwin"]:
        
        os.chmod(gecko_driver, 0o755)

    # Configure Firefox options
    options = Options()
    options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    options.set_preference("media.volume_scale", "0.0")
    options.set_preference("dom.webnotifications.enabled", False)

    user_agent = 'Mozilla/5.0 (X11; ; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
    options.set_preference("general.useragent.override", user_agent)

    if not load_images:
        options.set_preference('permissions.default.image', 2)
    
    if is_headless:
        options.add_argument('--headless')
    
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    # Initialize the WebDriver
    driver = webdriver.Firefox(service=Service(executable_path=gecko_driver), options=options)
    logger.info(driver)
    return driver