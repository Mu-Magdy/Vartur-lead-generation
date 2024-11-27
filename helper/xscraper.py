from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

from .config import init_driver, logger, XLoginError, InvalidCredentialsError
from .llm import evaluate_lead

class XScraper:
    def __init__(self, url, email, password, is_headless=False):
        self.url = url
        self.email = email
        self.password = password
        self.driver = init_driver(is_headless)
        self.main_post_content = None

    def _login(self):
        """Perform login on X"""
        try:
            logger.info("Navigating to X login page...")
            self.driver.get("https://X.com/i/flow/login")
            time.sleep(3)

            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
            )
            email_field.send_keys(self.email)
            logger.debug("Email entered.")
            
            # Click next
            next_button = self.driver.find_element(By.XPATH, "//span[text()='Next']")
            next_button.click()
            logger.debug("Clicked next button.")
            time.sleep(2)

            # Handle possible username verification
            try:
                username_verify = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']"))
                )
                username_verify.send_keys(self.email.split('@')[0])
                next_button = self.driver.find_element(By.XPATH, "//span[text()='Next']")
                next_button.click()
                logger.debug("Username verified.")
                time.sleep(2)
            except TimeoutException:
                logger.info("Username verification step skipped.")

            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            password_field.send_keys(self.password)
            logger.debug("Password entered.")
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//span[text()='Log in']")
            login_button.click()
            time.sleep(5)

            # Check for successful login
            if "login" in self.driver.current_url:
                error_message = self.driver.find_element(By.XPATH, "//span[contains(@class, 'error-message')]").text
                logger.error(f"Invalid credentials: {error_message}")
                raise InvalidCredentialsError(error_message)
            
            logger.info("Login successful.")

        except TimeoutException:
            logger.exception("Login process timeout.")
            raise XLoginError("Login process timeout")
        except Exception as e:
            logger.exception(f"Login failed: {str(e)}")
            raise XLoginError(f"Login failed: {str(e)}")

    def _navigate_to_post(self):
        """Navigate to the specific X post"""
        logger.info(f"Navigating to post: {self.url}")
        self.driver.get(self.url)
        time.sleep(5)
        # Extract main post content immediately after navigation
        self.main_post_content, self.main_username = self._get_tweet_content()

    def _scroll_to_load_comments(self):
        """Scroll down to load more comments"""
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        scroll_pause_time = 2
        max_scrolls = 50
        scrolls = 0
        
        logger.info("Beginning to scroll to load comments.")

        while scrolls < max_scrolls:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            
            # Break if no more content loaded
            if new_height == last_height:
                logger.info("No more content loaded, stopping scrolling.")
                break
                
            last_height = new_height
            scrolls += 1
        
        logger.info("Scrolling completed.")

    def _get_tweet_content(self):
        """Extract the main tweet text content"""
        try:
            # Wait for the main tweet to load
            main_tweet = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div"))
            )
            
            # Try multiple selectors
            try:
                content_element = main_tweet.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div"
                )
                logger.info("Content extracted using first selector.")
            except:
                try:
                    content_element = main_tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text.strip()
                    logger.info("Content extracted using second selector.")
                except:
                    content_element = ''
            
            try:
                username_element = main_tweet.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/a/div/span"
                )
                logger.info("Unsername extracted.")
            except:
                username_element = ''
            
            # Return text if found
            logger.info("Main tweet content extracted.")
            return content_element.text, username_element.text[1:]
            
        except Exception as e:
            logger.exception(f"Error extracting main tweet content: {str(e)}")
            return ""

    def _extract_comments(self):
        """Extract comments data from the post"""
        logger.info("Extracting comments from the post.")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        comments = soup.find_all('article', {'data-testid': 'tweet'})
        
        data = []
        for comment in comments:
            try:
                # Skip the main tweet
                if comment.find('a', {'aria-label': 'Profile Tweet time'}):
                    continue
                
                # Extract user info
                user_info = comment.find('div', {'data-testid': 'User-Name'})
                name = user_info.find('span', {'class': re.compile(r'css-.*')}).text.strip()
                username = user_info.find('a', {'role': 'link'})['href'].strip('/')
                
                # Extract comment content
                content_text = comment.find("div", class_="css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-bcqeeo r-1ttztb7 r-qvutc0 r-1qd0xha r-a023e6 r-rjixqe r-16dba41 r-bnwqim").text.strip()

                # Evaluate if this comment is a lead using the main post content
                is_lead, reason = evaluate_lead(
                    info=self.main_post_content,
                    user_comment=content_text,
                    platform='X'
                )
                if username != self.main_username:
                    data.append({
                        'Name': name,
                        'Username': username,
                        'Profile Link': f"https://x.com/{username}",
                        'Comment Content': content_text,
                        'Is Lead': is_lead,
                        'Reason': reason,
                    })
                
            except Exception as e:
                print(f"Error processing comment: {str(e)}")
                continue
        logger.info("Comments extraction complete.")
        return pd.DataFrame(data)

    def scrape(self):
        """Main function to perform the scraping process"""
        logger.info("Starting scraping process.")
        try:
            self._login()
            self._navigate_to_post()
            self._scroll_to_load_comments()
            return self._extract_comments()
        finally:
            self.driver.quit()
            logger.info("Scraping process completed and browser closed.")