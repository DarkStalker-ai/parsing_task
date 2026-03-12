"""
Script parses product data from brain.com.ua using Selenium.
"""
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException


from load_django import *
from parser_app.models import Product, Product_Image, Product_Characteristics

def launch_browser():

    """Launching browser"""

    firefox_options = webdriver.FirefoxOptions()

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.maximize_window()
    driver.implicitly_wait(5)

    print("Launching browser")
    return driver


def quit_driver(driver):

    """Close the browser"""

    print("Close the browser")
    driver.quit()


def search_product(driver):

    """
    1. Open Main page
    2. Enter query in the search bar
    3. Press button "Знайти"
    """

    print("\n=== Searching page ===")

    driver.get("https://brain.com.ua/")
    print("Open main page")
    sleep(2)

    try:
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='header-bottom-in']//input[@type='search']"))
        )
        search_input.clear()
        search_input.send_keys("Apple iPhone 15 128GB Black")
        print("Query is entered")
        sleep(1)

        search_input.send_keys(Keys.RETURN)
        print("Button is clicked")
        sleep(3)

    except TimeoutException:
        print("Search string isn't found")
        raise


def open_first_product(driver):

    """
    4: In the search results, click on the first result.
    """

    print("\n=== Opening the first one product ===")

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'br-pp-ipd-hidden')]"))
        )
        sleep(2)

        first_product = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class, 'br-pp-ipd-hidden')]//a)[1]"))
        )

        product_url = first_product.get_attribute('href')
        print(f"The first product URL: {product_url}")

        first_product.click()
        print("Go to the next page")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'desktop-only-title')]"))
        )
        sleep(2)

    except TimeoutException as e:
        print(f"Error: {e}")
        raise


def collect_product_data(driver):

    """
    5. Gather information about the product
    """

    print("\n=== Collecting data ===")

    product_data = {}

    """
    Full name
    """
    try:
        title = driver.find_element(By.XPATH,"//h1[contains(@class, 'desktop-only-title')]").text.strip()
        product_data['full_name'] = title
        print(f"Full name: {title}")
    except:
        product_data['full_name'] = None
        print("Name not found")

    """
    Code
    """
    try:
        main_container = driver.find_element(
            By.XPATH,
                    "//div[contains(@class, 'container') and contains(@class, 'product-content-wrapper')]"
        )
        code = main_container.get_attribute('data-code')
        product_data['code'] = code
        print(f"Code: {code}")
    except:
        try:
            code = driver.find_element(
                By.XPATH,
                        "//div[contains(@class, 'product-code-num')]//span[contains(@class, 'br-pr-code-val')]"
            ).text.strip()
            product_data['code'] = code
            print(f"Code: {code}")
        except:
            product_data['code'] = None
            print(" Code not found")

    """
    Color
    """
    url = driver.current_url
    if "Black" in url:
        product_data['color'] = "black"
    elif "Blue" in url:
        product_data['color'] = "blue"
    elif "Pink" in url:
        product_data['color'] = "pink"
    elif "Green" in url:
        product_data['color'] = "green"
    else:
        product_data['color'] = None
    print(f"Color: {product_data['color']}")

    """
    Memory capacity
    """
    try:
        memory = driver.find_element(
            By.XPATH,
                    "//div[contains(@class, 'current-product-series')]"
                    "//div[contains(@class, 'series-characteristic')]//a"
        ).text.strip()
        product_data['memory'] = memory
        print(f"Memory: {memory}")
    except:
        try:
            memory = driver.find_element(
                By.XPATH,
                        "//div[contains(@class, 'br-pr-chr-item')]//span[contains(text(), 'Вбудована пам')]"
                        "/following-sibling::span//a"
            ).text.strip()
            product_data['memory'] = memory
            print(f"Memory (from characteristics): {memory}")
        except:
            product_data['memory'] = None
            print("Memory not found")

    """
    Manufacturer
    """
    try:
        main_container = driver.find_element(
            By.XPATH, "//div[contains(@class, 'container') and contains(@class, 'product-content-wrapper')]"
        )
        manufacturer = main_container.get_attribute('data-vendor')
        product_data['manufacturer'] = manufacturer
        print(f"Manufacturer: {manufacturer}")
    except:
        product_data['manufacturer'] = None
        print("Manufacturer not found")

    """
    Prices
    """

    """
    Default price
    """

    try:
        default_price = driver.find_element(
            By.XPATH,
                    "//div[contains(@class, 'br-pr-op')]//div[contains(@class, 'price-wrapper')]/span"
        ).text.strip()
        default_price = float(default_price.replace(" ", "").replace("₴", ""))
        product_data['default_price'] = default_price
        print(f"Default price: {default_price}")
    except:
        product_data['default_price'] = None
        print("Default price not found")

    """
    Sale price
    """
    try:
        sale_price = driver.find_element(
            By.XPATH,
                    "//div[contains(@class, 'br-pr-np')]//span[contains(@class, 'red-price')]"
        ).text.strip()
        sale_price = float(sale_price.replace(" ", "").replace("₴", ""))
        product_data['sale_price'] = sale_price
        print(f"Sale price: {sale_price}")
    except:
        try:
            sale_price = driver.find_element(
                By.XPATH,
                        "//div[contains(@class, 'br-pr-np')]//div[contains(@class, 'price-wrapper')]/span"
            ).text.strip()
            sale_price = float(sale_price.replace(" ", "").replace("₴", ""))
            product_data['sale_price'] = sale_price
            print(f"Sale price: {sale_price}")
        except:
            product_data['sale_price'] = None
            print("Sale price not found")

    """
    Photos
    """
    try:
        images = []
        image_elements = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'br-pr-slider')]//img[contains(@class, 'br-main-img')]"
        )
        for img in image_elements:
            src = img.get_attribute("src")
            if src and src.startswith("http") and src not in images:
                images.append(src)

        product_data['images'] = images
        print(f"Photos: {len(images)} found")
    except:
        product_data['images'] = []
        print("Photos not found")

    """
    Expanding all characteristics
    """
    print("\n--- Expanding all characteristics ---")
    try:

        show_all_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'br-prs-button') and contains(., 'Всі характеристики')]")
            )
        )

        driver.execute_script("arguments[0].click();", show_all_button)
        print("Button 'Всі характеристики' clicked via JavaScript.")

        # Чекаємо на появу нових блоків
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'br-pr-chr-item')]"))
        )
        print("All characteristic blocks loaded.")
        sleep(1)

    except Exception as e:
        print(f"✗ All click methods failed: {e}")

    """
    Reviews count
    """
    import re
    try:
        reviews_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                        "//div[contains(@class, 'main-right-block')]//a[contains(@class, 'scroll-to-element')]/span"))
        )
        reviews_text = reviews_element.text.strip()
        reviews_match = re.search(r'(\d+)', reviews_text)
        product_data['reviews_count'] = int(reviews_match.group(1)) if reviews_match else 0
        print(f"Reviews count: {product_data['reviews_count']}")
    except TimeoutException:
        print("Reviews block not found within timeout.")
        product_data['reviews_count'] = 0

    """
    Screen diagonal
    """
    display_section = driver.find_element(
        By.XPATH,
                "//div[contains(@class, 'br-pr-chr-item') and .//h3[contains(text(), 'Дисплей')]]"
    )
    rows = display_section.find_elements(By.XPATH, ".//div[span]")

    try:
        for row in rows:
            spans = row.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 2:
                key = spans[0].text.strip().lower()
                if 'діагональ' in key or 'diagonal' in key:
                    links = spans[1].find_elements(By.TAG_NAME, "a")
                    product_data['screen_diagonal'] = links[0].text.strip() if links else spans[1].text.strip()
                    print(f"Screen diagonal: {product_data['screen_diagonal']}")
                    break
    except:
        product_data['screen_diagonal'] = None
        print("Screen diagonal not found")

    """
    Display resolution
    """
    try:
        for row in rows:
            spans = row.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 2:
                key = spans[0].text.strip().lower()
                if 'роздільна' in key or 'здатність' in key or 'resolution' in key:
                    links = spans[1].find_elements(By.TAG_NAME, "a")
                    product_data['display_resolution'] = links[0].text.strip() if links else spans[1].text.strip()
                    print(f"Display resolution: {product_data['display_resolution']}")
                    break
    except:
        product_data['display_resolution'] = None
        print("Display resolution not found")

    """
    All characteristic
    """
    print("\n--- Collecting characteristics ---")
    characteristics = {}

    try:
        char_blocks = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'br-pr-chr')]/div[contains(@class, 'br-pr-chr-item')]"
        )
        print(f"Found {len(char_blocks)} characteristic blocks")

        for block in char_blocks:
            try:
                block_title = block.find_element(By.XPATH, ".//h3").text.strip()
            except:
                block_title = "Загальні"

            char_rows = block.find_elements(By.XPATH, ".//div[span]")
            for row in char_rows:
                spans = row.find_elements(By.TAG_NAME, "span")
                if len(spans) >= 2:
                    key = spans[0].text.strip()
                    links = spans[1].find_elements(By.TAG_NAME, "a")
                    if links:
                        values = [link.text.strip() for link in links if link.text.strip()]
                        value = ", ".join(values)
                    else:
                        value = spans[1].text.strip()

                    value = re.sub(r'\s+', ' ', value).strip()

                    if key and value and key != value:
                        full_key = f"{block_title}: {key}" if block_title != "Загальні" else key
                        characteristics[full_key] = value

        product_data['characteristics'] = characteristics
        print(f"✓ Characteristics collected: {len(characteristics)}")

    except Exception as e:
        product_data['characteristics'] = {}
        print(f"✗ Error collecting characteristics: {e}")

    return product_data

# def debug_display_block(driver):
#     """Діагностика блоку дисплею"""
#     print("\n=== DEBUG: Display block ===")
#
#     try:
#         display_block = driver.find_element(By.XPATH,
#                                             "//div[contains(@class, 'br-pr-chr-item') and .//h3[contains(text(), 'Дисплей')]]")
#         print("✓ Display block found")
#
#         rows = display_block.find_elements(By.XPATH, ".//div[span]")
#         print(f"Found {len(rows)} rows in display block")
#
#         for i, row in enumerate(rows, 1):
#             spans = row.find_elements(By.TAG_NAME, "span")
#             if len(spans) >= 2:
#                 key = spans[0].text.strip()
#                 value = spans[1].text.strip()
#                 print(f"  Row {i}: '{key}' = '{value}'")
#
#     except Exception as e:
#         print(f"✗ Error: {e}")


def print_product_data(product_data):

    """
    Output of the data
    """

    print("\n" + "="*70)
    print("PARSING RESULTS".center(70))
    print("="*70)

    print(f"\n PRODUCT:")
    print(f"  Full name: {product_data.get('full_name')}")
    print(f"  Code: {product_data.get('code')}")
    print(f"  Manufacturer: {product_data.get('manufacturer')}")
    print(f"  Color: {product_data.get('color')}")
    print(f"  Memory: {product_data.get('memory')}")

    print(f"\n PRICES:")
    print(f"  Default: {product_data.get('default_price')} ₴")
    print(f"  Sale: {product_data.get('sale_price')} ₴")

    print(f"\n DISPLAY:")
    print(f"  Diagonal: {product_data.get('screen_diagonal')}")
    print(f"  Resolution: {product_data.get('display_resolution')}")

    print(f"\n REVIEWS:")
    print(f"  Count: {product_data.get('reviews_count')}")

    images = product_data.get('images', [])
    print(f"\n PHOTOS ({len(images)}):")
    for i, img in enumerate(images[:5], 1):
        print(f"  {i}. {img}")
    if len(images) > 5:
        print(f"  ... and {len(images) - 5} more")

    chars = product_data.get('characteristics', {})
    print(f"\n CHARACTERISTICS ({len(chars)}):")
    for i, (key, value) in enumerate(list(chars.items())[:15], 1):
        print(f"  {key}: {value}")
    if len(chars) > 15:
        print(f"  ... and {len(chars) - 15} more")

    print("\n" + "="*70)


def save_to_database(product_data):

    """
    Stores collected data in PostgreSQL via Django ORM
    """

    print("\n--- Saving to Database ---")

    product, created = Product.objects.update_or_create(
        code=product_data.get('code'),
        defaults={
            'full_name': product_data.get('full_name'),
            'color': product_data.get('color'),
            'memory': product_data.get('memory'),
            'manufacturer': product_data.get('manufacturer'),
            'default_price': product_data.get('default_price'),
            'sale_price': product_data.get('sale_price'),
            'reviews_count': product_data.get('reviews_count', 0),
            'screen_diagonal': product_data.get('screen_diagonal'),
            'display_resolution': product_data.get('display_resolution'),
        }
    )

    action = "Created" if created else "Updated"
    print(f"{action} product: {product.full_name}")

    Product_Image.objects.filter(product=product).delete()

    images = product_data.get('images', [])
    for img_url in images:
        Product_Image.objects.create(
            product=product,
            url=img_url
        )
    print(f"{len(images)} photos are saved")

    Product_Characteristics.objects.filter(product=product).delete()

    characteristics = product_data.get('characteristics', {})
    for key, value in characteristics.items():
        Product_Characteristics.objects.create(
            product=product,
            key=key,
            value=value
        )
    print(f"{len(characteristics)} characteristics are saved")

    print("Successfully saved to PostgreSQL!")
    return product

def main():

    """
    Main function
    """

    driver = None
    try:
        driver = launch_browser()
        search_product(driver)
        open_first_product(driver)
        product_data = collect_product_data(driver)
        print_product_data(product_data)
        save_to_database(product_data)
        sleep(3)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.save_screenshot("error.png")
    finally:
        if driver:
            quit_driver(driver)


if __name__ == '__main__':
    main()