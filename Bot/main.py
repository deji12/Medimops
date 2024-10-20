import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from gologin import GoLogin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .config import *
from Core.models import BotControl, ProductMaxPrice
import re
from decimal import Decimal

class Bot:
    def __init__(self, email, password, gologin_token, profile_id, headless=True):
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Initializing Bot with GoLogin profile...{ENDC}")

        # Setting parameters
        self.email = email
        self.password = password
        self.login_url = "https://www.medimops.de/Mein-Konto/"
        self.wishlist_url = "https://www.medimops.de/MeinMerkzettel/"
        self.cart_url = "https://www.medimops.de/Warenkorb/"
        self.control = BotControl.objects.last()

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKBLUE}Initializing GoLogin with profile ID: {profile_id}{ENDC}")
        # Initialize GoLogin
        self.gl = GoLogin({
            "token": gologin_token,
            "profile_id": profile_id,
            "profile_path": PROFILE_PATH
        })

        # Get the debugger address to attach Selenium to GoLogin profile
        debugger_address = self.gl.start()

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKBLUE}Starting Chrome with GoLogin debugger address: {debugger_address}{ENDC}\n\n")
        # Set Chrome options to connect to GoLogin's profile
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        chrome_options.binary_location = '/usr/bin/google-chrome'

        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")  # Required for running headlessly on some platforms
            chrome_options.add_argument("--no-sandbox")   # Required for running inside containers
            chrome_options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems
        

        # Initialize the driver with the GoLogin profile
        self.driver = webdriver.Chrome(service=CHROME_DRIVER_SERVICE, options=chrome_options)

    def __handle_consent_popup(self):
        """Handle the consent popup using JavaScript execution."""
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKBLUE}Handling consent popup...{ENDC}")
        try:
            # Wait for the page to load and the popup to appear
            time.sleep(5)

            # Execute the JavaScript to handle the consent popup
            self.driver.execute_script("""
                const shadowHost = document.querySelector('#cmpwrapper');
                const shadowRoot = shadowHost.shadowRoot;
                const consentButton = shadowRoot.querySelector('#cmpwelcomebtnyes a.cmpboxbtnyes');
                if (consentButton) {
                    consentButton.click();
                }
            """)

            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKGREEN}Consent popup handled successfully.{ENDC}")

        except Exception as e:
            print(f"🤖{WARNING} [LOG] {ENDC}-> {FAIL}Error handling consent popup: {e}{ENDC}")

    def login(self):
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Logging in to account...{ENDC}")

        self.driver.get(self.login_url)
        self.__handle_consent_popup()

        try:
            # Insert username
            enter_email = self.driver.find_element(By.NAME, "lgn_usr")
            enter_email.send_keys(self.email)
            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKGREEN}Entered email successfully.{ENDC}")

            # Insert password
            enter_password = self.driver.find_element(By.NAME, "lgn_pwd")
            enter_password.send_keys(self.password)
            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKGREEN}Entered password successfully.{ENDC}")

            # Hit the return key and submit login details
            enter_password.send_keys(Keys.RETURN)
            time.sleep(5)
            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKGREEN}Login submitted.{ENDC}")

        except Exception as e:
            print(f"🤖{WARNING} [LOG] {ENDC}-> {FAIL}Login error: {e}{ENDC}")

    def __add_wishlist_items_to_cart(self):
        """Retrieve products where the back again email switch is on and add them to the cart."""

        ITEM_MAX_PRICE = self.control.max_price
        
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Navigating to wishlist page...{ENDC}")
        self.driver.get(self.wishlist_url)
        time.sleep(10)  # Wait for the wishlist page to load

        try:
            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Adding wishlist items to cart...{ENDC}")

            # Execute JavaScript to handle the products
            self.driver.execute_script("""
                var ITEM_MAX_PRICE = arguments[0];
                var products = document.querySelectorAll('.notice-list-product__grid');
                
                products.forEach(function(product) {
                    product.scrollIntoView(true);
                    var switchBox = product.querySelector('.switch__box');
                    if (switchBox && switchBox.classList.contains('switch__box--on')) {
                        var priceElement = product.querySelector('.notice-list-product__price');
                        if (priceElement) {
                            var priceText = priceElement.textContent.replace('€', '').replace(',', '.').trim();
                            var price = parseFloat(priceText);
                            if (price <= ITEM_MAX_PRICE) {
                                var addToCartButton = product.querySelector('a.add-to-cart.add-to-cart__main');
                                if (addToCartButton) {
                                    addToCartButton.scrollIntoView(true);
                                    addToCartButton.click();
                                    setTimeout(function() {}, 5000);
                                }
                            }
                        }
                    }
                });
            """, ITEM_MAX_PRICE)

            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKGREEN}Wishlist items added to cart.{ENDC}")
            time.sleep(5)

        except Exception as e:
            print(f"🤖{WARNING} [LOG] {ENDC}-> {FAIL}Error adding wishlist items to cart: {e}{ENDC}")

    def __get_product_urls_from_wishlist(self):

        """Retrieve product URLs where the back again email switch is on."""

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Navigating to wishlist page...{ENDC}")
        self.driver.get(self.wishlist_url)
        time.sleep(10)  #

        # Find all product containers
        products = self.driver.find_elements(By.CLASS_NAME, "notice-list-product__grid")

        active_product_urls = []

        # Loop through each product container
        for product in products:
            # Check if the product has an active switch (switch__box--on)
            switch_box = product.find_element(By.CLASS_NAME, "switch__box")
            if "switch__box--on" in switch_box.get_attribute("class"):

                # Extract the name of the product
                name_element = product.find_element(By.XPATH, './/div[@class="notice-list-product__title"]')
                product_name = name_element.text

                # make sure price is not greater than limit
                price_element = product.find_element(By.XPATH, './/span[@class="notice-list-product__price"]')
                price_text = price_element.text

                # Use a regular expression to extract only the numeric part (integer or float)
                price_number = re.findall(r"\d+,\d+|\d+", price_text)[0].replace(",", ".")
                price_value = float(price_number)

                try:
                    # check if max price exists for product
                    product_max_price = ProductMaxPrice.objects.get(item_name=product_name, status=True)
                    if Decimal(price_value) <= product_max_price:
                        # Extract the URL of the product
                        product_link = product.find_element(By.TAG_NAME, "a")  # Adjust if necessary
                        url = product_link.get_attribute("href")
                        active_product_urls.append(url)

                except ProductMaxPrice.DoesNotExist:

                    # Product has no max price set
                    product_link = product.find_element(By.TAG_NAME, "a")  # Adjust if necessary
                    url = product_link.get_attribute("href")
                    active_product_urls.append(url)

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Processing {len(active_product_urls)} products...{ENDC}")

        return active_product_urls
    
    def add_products_to_cart(self):

        products = self.__get_product_urls_from_wishlist()

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Adding product variants to cart...{ENDC}")

        for product_url in products:
            # Go to the product page
            self.driver.get(product_url)
            
            time.sleep(3)  # Wait for the page to load (adjust as necessary)

            script = '''
                var variantLinks = document.getElementsByClassName('variant-select__variant');
                for (var i = 0; i < variantLinks.length; i++) {
                    variantLinks[i].click();  // Click each variant
                    
                    // Scroll to and click the "Add to Cart" button
                    var addToCartButton = document.querySelector('.add-to-cart');
                    if (addToCartButton) {
                        addToCartButton.scrollIntoView();
                        addToCartButton.click();
                        console.log('Clicked variant ' + (i + 1) + ' and added to cart.');
                    } else {
                        console.log('Add to Cart button not found for variant ' + (i + 1));
                    }
                    
                    // Delay in-between clicks (simulating wait)
                    var start = new Date().getTime();
                    var end = start;
                    while (end < start + 5000) {  // 5-second wait
                        end = new Date().getTime();
                    }
                }
            '''
            
            # Execute the script in Selenium
            self.driver.execute_script(script)

            print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Added product variants to cart successfully{ENDC}")

    def max_out_cart_items(self):
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Maxing out cart item quantities...{ENDC}")

        self.driver.get(self.cart_url)
        time.sleep(5)

        # Define JavaScript to handle quantity increase with a promise
        js_code = r"""
            function waitFor(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

            async function incrementProduct(product, index) {
                let increaseButton = product.querySelector('.checkout-product__button__decrease');
                let previousError = false;
                let maxReached = false;
                let incrementCount = 1; // Initialize the increment counter
                const maxIncrements = """ + str(MAX_PRODUCT_INCREMENTS) + r""";  

                while (!maxReached && incrementCount < maxIncrements) {
                    increaseButton.click();
                    await waitFor(3000); // Short wait time after clicking

                    // Check for global error message
                    let errorMessage = document.querySelector('.msg--error');
                    if (errorMessage && errorMessage.style.display !== 'none') {
                        if (!previousError) {
                            console.log("Max quantity reached for product " + (index + 1));
                            previousError = true;
                            errorMessage.style.display = 'none';
                            maxReached = true;
                        }
                    } else {
                        previousError = false;
                    }

                    incrementCount++; // Increase the increment counter
                    console.log("Incremented product " + (index + 1) + " " + incrementCount + " times.");

                    await waitFor(1000); // Wait before the next click attempt
                }
            }

            // Get all products on the page
            const products = document.querySelectorAll('.checkout-product');

            // Loop through all products and increment their quantity
            for (let i = 0; i < products.length; i++) {
                await incrementProduct(products[i], i); // Run sequentially
            }

            // Indicate that the script is done
            const doneIndicator = document.createElement('div');
            doneIndicator.id = 'incrementDone';
            document.body.appendChild(doneIndicator);
            console.log('All products processed.'); // Final log statement
        """

        try:
            self.driver.execute_script(js_code)
            print("🤖 Max quantity reached for all products in the cart.")
        except Exception as e:
            if "script timeout" in str(e).lower():  # Check for timeout specifically
                print("🤖 Script timed out, waiting for completion...")
                WebDriverWait(self.driver, 5000).until(
                    EC.presence_of_element_located((By.ID, 'incrementDone'))
                )
                print("🤖 Script completed successfully after timeout.")
            else:
                print(f"🤖 Error maxing out cart items: {e}")

    def checkout(self):

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Proceeding to checkout...{ENDC}")

        # click checkout button
        checkout_button = self.driver.find_element(By.CLASS_NAME, 'cart-page__checkout-button')
        checkout_button.click()

        time.sleep(5)

        # click the proceed button
        proceed_to_checkout_button = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'checkout-navigation-buttons__button-next'))
        )
        proceed_to_checkout_button.click()

        # Wait for the radio input element to be present
        radio_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'payment-fcpocreditcard'))
        )

        radio_input.click()

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Selected card payment for checkout...{ENDC}")
        time.sleep(10) # wait for form to render

        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Inputing card details...{ENDC}")

        # Wait and fill in the card type
        card_type_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'cardType'))
        )
        card_type_select.send_keys(self.control.card_type)

        time.sleep(2)

        # Wait for the account holder field and fill it in
        account_holder_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'fcpo_kkname'))
        )
        
        account_holder_input.send_keys(Keys.CONTROL + "a")  # Select all text
        account_holder_input.send_keys(Keys.DELETE)  # Delete the selected text
        account_holder_input.send_keys(self.control.card_holder_name)

        time.sleep(2)

        # Wait for the card number field (iframe) and fill it in
        card_number_iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='cardpan']/iframe"))
        )
        self.driver.switch_to.frame(card_number_iframe)
        card_number_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        card_number_input.clear()
        card_number_input.send_keys(self.control.card_number)
        self.driver.switch_to.default_content()

        time.sleep(2)

        # Wait for the expiry month field (iframe) and fill it in
        expiry_month_iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='cardexpiremonth']/iframe"))
        )
        self.driver.switch_to.frame(expiry_month_iframe)

        time.sleep(2)

        # Wait and fill in the card type
        expiry_month_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'cardexpiremonth'))
        )
        expiry_month_input.send_keys(str(self.control.expiration_month))

        self.driver.switch_to.default_content()

        time.sleep(2)

        # Wait for the expiry year field (iframe) and fill it in
        expiry_year_iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='cardexpireyear']/iframe"))
        )
        self.driver.switch_to.frame(expiry_year_iframe)
        expiry_year_input =  WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'cardexpireyear'))
        )
        expiry_year_input.send_keys(str(self.control.expiration_year))
        
        self.driver.switch_to.default_content()

        time.sleep(2)

        # Wait for the CVV field (iframe) and fill it in
        cvv_iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='cardcvc2']/iframe"))
        )
        self.driver.switch_to.frame(cvv_iframe)
        cvv_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'cardcvc2'))
        )
        cvv_input.clear()
        cvv_input.send_keys(str(self.control.cvv))

        self.driver.switch_to.default_content()

        time.sleep(5)
        checkout_button = self.driver.find_element(By.CLASS_NAME, 'checkout-navigation-buttons__button-next')
        checkout_button.click()

        time.sleep(10)
        # click buy now button
        checkout_button = self.driver.find_element(By.CLASS_NAME, 'checkout-navigation-buttons__button-next')
        checkout_button.click()

        time.sleep(100)

    def stop(self):
        """Stop the GoLogin profile session."""
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKCYAN}Stopping the bot and GoLogin session...{ENDC}")
        self.driver.quit()
        self.gl.stop()
        print(f"🤖{WARNING} [LOG] {ENDC}-> {OKGREEN}Bot stopped successfully.{ENDC}")

    def run(self):
        self.login()
        self.add_products_to_cart()
        self.max_out_cart_items()
        self.checkout()
        self.stop()

# Instantiate and use the bot
# bot = Bot(EMAIL, PASSWORD, GOLOGIN_TOKEN, PROFILE_ID)
# bot.run()
