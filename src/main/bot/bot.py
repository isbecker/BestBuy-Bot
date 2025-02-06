import logging
from enum import Enum, auto

from selenium.common.exceptions import NoSuchElementException, TimeoutException
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

    def run(self):
        while self.state != BotState.COMPLETE:
            if self.state == self.desired_end_state:
                logging.info(f"Reached desired end state: {self.desired_end_state}")
                break

            logging.info(f"Current state: {self.state}")

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
        logging.info(f"Transitioning from {self.state} to {new_state}.")
        self.state = new_state

    def login(self):
        """Logs in, then transitions to adding to cart."""
        logging.info("Logging in")
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
            logging.info("An item was already bought. Skipping purchase steps.")
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
        logging.info(f"Navigated to saved items page: {saved_items_url}")

        try:
            # Wait until the saved items panel is visible.
            saved_items_panel = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, "saveditems-recentlyviewed-tabpanel")
                )
            )
            logging.info("Saved items panel loaded.")

            # Wait until the saved items are loaded inside the panel.
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "#saveditems-recentlyviewed-tabpanel li.grid-card",
                    )
                )
            )
            logging.info("Saved items loaded inside the panel.")

            # Find all saved item cards.
            saved_items = saved_items_panel.find_elements(
                By.CSS_SELECTOR, "li.grid-card"
            )
            logging.info(f"Found {len(saved_items)} saved item(s).")

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
                        logging.info(
                            f"Item {item_url} add-to-cart button is not enabled."
                        )
                except TimeoutException:
                    logging.info(
                        "Item details not fully loaded or add-to-cart button not clickable."
                    )
                except Exception as e:
                    logging.error(f"Error processing saved item: {e}")

            # Check items based on priority ordering
            for index, item_url in enumerate(priority_urls):
                if item_url in item_elements:
                    atc_button = item_elements[item_url]
                    logging.info(f"Checking item {index+1}: {item_url}")

                    try:
                        atc_button.click()
                        logging.info(f"Item {index+1}: Add-to-cart button clicked.")
                        self.transition_to_state(BotState.CHECKOUT)
                        return  # Exit after a successful click.
                    except Exception as e:
                        logging.error(
                            f"Error clicking add-to-cart button for item {index+1}: {e}"
                        )

            logging.info("No available saved items could be added to cart.")
        except TimeoutException as e:
            logging.error(f"Saved items panel did not load in time: {e}")

    def checkout(self):
        """Attempts to start the checkout process."""
        if self.item_already_bought:
            logging.info("An item was already bought. Skipping purchase steps.")
            self.transition_to_state(BotState.COMPLETE)
            return

        # Proceed to the cart page to checkout.
        self.driver.get("https://www.bestbuy.com/cart")
        try:
            logging.info("Attempting to checkout.")
            # Check if the cart is empty
            cart_app = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "cartApp"))
            )
            cart_items = cart_app.find_elements(By.CSS_SELECTOR, "ul.item-list li")
            if not cart_items:
                logging.info("Cart is empty. Returning to saved items page.")
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
            logging.info("Checkout button clicked. Transitioning to PLACE_ORDER state.")
            self.transition_to_state(BotState.PLACE_ORDER)
        except Exception as e:
            logging.error(f"Error during checkout: {e}")

    def place_order(self):
        """Attempt to place the order for the current product."""
        if self.item_already_bought:
            logging.info("An item was already bought. Skipping purchase steps.")
            self.transition_to_state(BotState.COMPLETE)
            return

        self.driver.get(self.config.links[0].url)
        try:
            logging.info("Attempting to place order.")
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
            logging.info(
                "Order successfully placed. No further purchases will be made."
            )
        except Exception as e:
            logging.error(f"Error during placing order: {e}")


def run(config: InfoConfig = config, desired_end_state: BotState = BotState.COMPLETE):
    bot = Bot(config, desired_end_state)
    bot.run()
