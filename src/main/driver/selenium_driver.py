import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SeleniumDriver(object):
    def __init__(
        self,
    ):
        self.driver = uc.Chrome(headless=False)

    def close_all(self):
        # close all open tabs
        if len(self.driver.window_handles) < 1:
            return
        for window_handle in self.driver.window_handles[:]:
            self.driver.switch_to.window(window_handle)
            self.driver.close()

    def login(self, email, password):
        self.driver.get("https://www.bestbuy.com/identity/global/signin")
        # involves checkbox selection
        # fill in email and password
        emailField = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "fld-e"))
        )
        emailField.send_keys(email)

        # check "Keep me signed in." box
        kmBox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/section/main/div[2]/div/div/div[1]/div/div/div/div/div/form/div[2]/div/span/input",
                )
            )
        )
        if not kmBox.is_selected():
            kmBox.click()

        # click Continue button
        cntBtn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/section/main/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/button",
                )
            )
        )
        cntBtn.click()

        # select "Use Password" radio
        upRd = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "password-radio"))
        )
        upRd.click()

        pwField = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "fld-p1"))
        )
        pwField.send_keys(password)

        # click Continue button
        signInBtn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/section/main/div[2]/div/div/div[1]/div/div/div/div/div/form/div[3]/button[1]",
                )
            )
        )
        signInBtn.click()

        # waiting to return to homepage
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "suggestViewClientComponent"))
        )
