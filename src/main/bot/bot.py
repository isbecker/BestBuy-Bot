import logging
import time
from enum import Enum, auto

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import InfoConfig, config
from ..driver import driver

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BotState(Enum):
    NOT_STARTED = auto()
    LOGIN = auto()
    ADD_TO_CART = auto()
    CHECKOUT = auto()
    PLACE_ORDER = auto()
    COMPLETE = auto()


class Bot:
    def __init__(
        self,
        config: InfoConfig,
        desired_end_state: BotState = BotState.COMPLETE,
    ):
        self.config = config
        self.selenium_object = driver
        self.driver = self.selenium_object.driver
        self.state = BotState.NOT_STARTED
        self.desired_end_state = desired_end_state
        self.item_already_bought = False  # Tracks if an item has been fully purchased

        # Track which URL we're on:
        self.url_index = 0
        self.weighted_urls = self._generate_weighted_urls()

    def _generate_weighted_urls(self):
        """Generate a list of URLs based on their weights."""
        weighted_urls = []
        for link_config in self.config.links:
            weighted_urls.extend([link_config.url] * link_config.weight)

        # Ensure the URLs are ordered correctly based on their weights
        ordered_urls = []
        while weighted_urls:
            for link_config in self.config.links:
                if link_config.url in weighted_urls:
                    ordered_urls.append(link_config.url)
                    weighted_urls.remove(link_config.url)
        return ordered_urls

    def run(self):
        while self.state != BotState.COMPLETE:
            if self.state == self.desired_end_state:
                logging.info(f"Reached desired end state: {self.desired_end_state}")
                break

            if self.state == BotState.NOT_STARTED:
                logging.info("Bot not started. Transitioning to LOGIN.")
                self.state = BotState.LOGIN
            elif self.state == BotState.LOGIN:
                self.login()
            elif self.state == BotState.ADD_TO_CART:
                self.add_to_cart()
            elif self.state == BotState.CHECKOUT:
                self.checkout()
            elif self.state == BotState.PLACE_ORDER:
                self.place_order()

    def login(self):
        """Logs in, then starts processing URLs one by one."""
        logging.info("Logging in")
        self.selenium_object.login(self.config.email, self.config.password)
        self.state = BotState.ADD_TO_CART

    def add_to_cart(self):
        """Attempts to add to cart on the current URL before moving on."""
        if self.item_already_bought:
            logging.info("An item was already bought. Skipping purchase steps.")
            self.state = BotState.COMPLETE
            return

        for _ in range(len(self.weighted_urls)):
            self.driver.get(self.weighted_urls[self.url_index])
            try:
                logging.info(f"Attempting to add to cart for URL #{self.url_index}")
                atcBtn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button"))
                )
                atcBtn.click()
                logging.info("Add to cart button clicked")

                self.state = BotState.CHECKOUT
                return
            except TimeoutException as e:
                logging.error(f"Timeout adding to cart for URL #{self.url_index}: {e}")
                self.url_index = (self.url_index + 1) % len(self.weighted_urls)

    def checkout(self):
        """Attempts to start the checkout process."""
        if self.item_already_bought:
            logging.info("An item was already bought. Skipping purchase steps.")
            self.state = BotState.COMPLETE
            return

        for _ in range(len(self.weighted_urls)):
            self.driver.get("https://www.bestbuy.com/cart")
            try:
                logging.info(f"Attempting to checkout for URL #{self.url_index}")
                checkoutBtn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/main/div/div[2]/div/div[1]/div/div[1]/div[1]/section[2]/div/div/div[3]/div/div[1]/button",
                        )
                    )
                )
                checkoutBtn.click()
                logging.info("Successfully added to cart - beginning checkout")
                self.state = BotState.PLACE_ORDER
                return
            except Exception as e:
                logging.error(f"Error during checkout for URL #{self.url_index}: {e}")
                self.url_index = (self.url_index + 1) % len(self.weighted_urls)

    def place_order(self):
        """Attempt to place the order for the current URL's product."""
        if self.item_already_bought:
            logging.info("An item was already bought. Skipping purchase steps.")
            self.state = BotState.COMPLETE
            return

        for _ in range(len(self.weighted_urls)):
            self.driver.get(self.weighted_urls[self.url_index])
            try:
                logging.info(f"Attempting to place order for URL #{self.url_index}")
                cvvField = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".summary-tile__cvv-code-input")
                    )
                )
                cvvField.send_keys(self.config.cvv)

                placeOrderBtn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div[2]/div/div[2]/div[1]/div[1]/main/div[3]/div[1]/div/div[4]/section/div/div/div[2]/div/button",
                        )
                    )
                )
                placeOrderBtn.click()

                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".thank-you-enhancement__info")
                    )
                )

                self.item_already_bought = True
                self.state = BotState.COMPLETE
                logging.info(
                    "Order successfully placed. No further purchases will be made."
                )
                return
            except Exception as e:
                logging.error(
                    f"Error during placing order for URL #{self.url_index}: {e}"
                )
                self.url_index = (self.url_index + 1) % len(self.weighted_urls)


def run(config: InfoConfig = config, desired_end_state: BotState = BotState.COMPLETE):
    bot = Bot(config, desired_end_state)
    bot.run()
