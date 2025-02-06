from loguru import logger
from enum import Enum, auto

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import InfoConfig, config
from ..driver import SeleniumDriver


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
        self.selenium_object = (
            SeleniumDriver(chromium_version=config.chromium_version)
            if config.chromium_version
            else SeleniumDriver()
        )  # Handle optional chromium_version
        self.driver = self.selenium_object.driver
        self.state = BotState.NOT_STARTED
        self.desired_end_state = desired_end_state
        self.item_already_bought = False  # Tracks if an item has been fully purchased
        self.chromium_version = config.chromium_version  # New property

    def run(self):
        while self.state != BotState.COMPLETE:
            if self.state == self.desired_end_state:
                logger.info(f"Reached desired end state: {self.desired_end_state}")
                break

            logger.info(f"Current state: {self.state}")

            if self.state == BotState.NOT_STARTED:
                self.transition_to_state(BotState.LOGIN)
            elif self.state == BotState.LOGIN:
                self.login()
            elif self.state == BotState.ADD_TO_CART:
                self.add_to_cart()
            elif self.state == BotState.CHECKOUT:
                self.checkout()
            elif self.state == BotState.PLACE_ORDER:
                self.place_order()

    def transition_to_state(self, new_state: BotState):
        logger.info(f"Transitioning from {self.state} to {new_state}.")
        self.state = new_state

    def login(self):
        """Logs in, then transitions to adding to cart."""
        logger.info("Logging in")
        self.selenium_object.login(self.config.email, self.config.password)
        self.transition_to_state(BotState.ADD_TO_CART)

    def add_to_cart(self):
        """
        Instead of visiting each product page one by one, load the saved items
        page and loop through the items in the "saveditems-recentlyviewed-tabpanel"
        container. For each saved item, check if its URL is in the priority list,
        then wait for its add-to-cart button (which must be enabled) before clicking.
        """
        if self.item_already_bought:
            logger.info("An item was already bought. Skipping purchase steps.")
            self.transition_to_state(BotState.COMPLETE)
            return

        # Load the saved items page.
        # Optionally, you can provide the URL via configuration.
        saved_items_url = (
            self.config.saved_items_url
            if hasattr(self.config, "saved_items_url")
            else "https://www.bestbuy.com/site/customer/lists/manage/saveditems"
        )
        self.driver.get(saved_items_url)
        logger.info(f"Navigated to saved items page: {saved_items_url}")

        try:
            # Wait until the saved items panel is visible.
            saved_items_panel = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, "saveditems-recentlyviewed-tabpanel")
                )
            )
            logger.info("Saved items panel loaded.")

            # Wait until the saved items are loaded inside the panel.
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "#saveditems-recentlyviewed-tabpanel li.grid-card",
                    )
                )
            )
            logger.info("Saved items loaded inside the panel.")

            # Find all saved item cards.
            saved_items = saved_items_panel.find_elements(
                By.CSS_SELECTOR, "li.grid-card"
            )
            logger.info(f"Found {len(saved_items)} saved item(s).")

            # Build a list of priority URLs from your configuration.
            sorted_links = sorted(
                self.config.links, key=lambda x: x.weight, reverse=True
            )
            priority_urls = [link_config.url for link_config in sorted_links]

            # Create a dictionary to map item URLs to their elements
            item_elements = {}
            for item in saved_items:
                try:
                    link_element = WebDriverWait(item, 2).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div.card-title a.clamp")
                        )
                    )
                    item_url = link_element.get_attribute("href")
                    atc_button = WebDriverWait(item, 5).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "button.add-to-cart-button")
                        )
                    )
                    # check if the add-to-cart button is enabled
                    if atc_button.is_enabled():
                        item_elements[item_url] = atc_button
                    else:
                        logger.info(
                            f"Item {item_url} add-to-cart button is not enabled."
                        )
                except TimeoutException:
                    logger.info(
                        "Item details not fully loaded or add-to-cart button not clickable."
                    )
                except Exception as e:
                    logger.error(f"Error processing saved item: {e}")

            # Check items based on priority ordering
            for index, item_url in enumerate(priority_urls):
                if item_url in item_elements:
                    atc_button = item_elements[item_url]
                    logger.info(f"Checking item {index+1}: {item_url}")

                    try:
                        atc_button.click()
                        logger.info(f"Item {index+1}: Add-to-cart button clicked.")
                        self.transition_to_state(BotState.CHECKOUT)
                        return  # Exit after a successful click.
                    except Exception as e:
                        logger.error(
                            f"Error clicking add-to-cart button for item {index+1}: {e}"
                        )

            logger.info("No available saved items could be added to cart.")
        except TimeoutException as e:
            logger.error(f"Saved items panel did not load in time: {e}")

    def checkout(self):
        """Attempts to start the checkout process."""
        if self.item_already_bought:
            logger.info("An item was already bought. Skipping purchase steps.")
            self.transition_to_state(BotState.COMPLETE)
            return

        # Proceed to the cart page to checkout.
        self.driver.get("https://www.bestbuy.com/cart")
        try:
            logger.info("Attempting to checkout.")
            # Check if the cart is empty
            cart_app = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "cartApp"))
            )
            cart_items = cart_app.find_elements(By.CSS_SELECTOR, "ul.item-list li")
            if not cart_items:
                logger.info("Cart is empty. Returning to saved items page.")
                self.transition_to_state(BotState.ADD_TO_CART)
                return

            checkoutBtn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "div.checkout-buttons__checkout button.btn-primary",
                    )
                )
            )
            checkoutBtn.click()
            logger.info("Checkout button clicked. Transitioning to PLACE_ORDER state.")
            self.transition_to_state(BotState.PLACE_ORDER)
        except Exception as e:
            logger.error(f"Error during checkout: {e}")

    def place_order(self):
        """Attempt to place the order for the current product."""
        if self.item_already_bought:
            logger.info("An item was already bought. Skipping purchase steps.")
            self.transition_to_state(BotState.COMPLETE)
            return

        self.driver.get(self.config.links[0].url)
        try:
            logger.info("Attempting to place order.")
            cvvField = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".summary-tile__cvv-code-input")
                )
            )
            cvvField.send_keys(self.config.cvv)

            placeOrderBtn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "div.payment__order-summary button.btn-primary",
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
            self.transition_to_state(BotState.COMPLETE)
            logger.info("Order successfully placed. No further purchases will be made.")
        except Exception as e:
            logger.error(f"Error during placing order: {e}")


def run(config: InfoConfig = config, desired_end_state: BotState = BotState.COMPLETE):
    bot = Bot(config, desired_end_state)
    bot.run()
