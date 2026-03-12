"""
Script parses product data from brain.com.ua using Playwright.
"""
import asyncio

from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright

from load_django import *
from parser_app.models import Product, Product_Image, Product_Characteristics


async def search_product(page):

    print("\n=== Searching page ===")

    await page.goto("https://brain.com.ua/", timeout=60000)

    print("Open main page")


    search_input = page.locator("//div[@class='header-bottom-in']//input[@type='search']")
    await search_input.fill("Apple iPhone 15 128GB Black", timeout=10000)
    await asyncio.sleep(2)
    print("Query is entered")
    await asyncio.sleep(2)

    try:
        search_button = page.locator("//div[@class='header-bottom-in']//input[@class='qsr-submit']").first
        await search_button.click(timeout=3000)
        print("Clicked search button")
    except Exception as e:
        print(f"Search button not found or error: {e}")
        await search_input.press("Enter")
        print("Pressed Enter in search field")

    try:
        # Очікуємо появи результатів пошуку
        await page.wait_for_selector("//div[contains(@class,'br-pp-ipd-hidden')]", timeout=10000)
        print("Search results loaded")
    except Exception as e:
        print(f"Error waiting for search results: {e}")
        # Перевіряємо, чи є результати пошуку
        no_results = page.locator("text=Нічого не знайдено")
        if await no_results.count() > 0:
            print("No products found")
        else:
            print("Page loaded but results selector not found")

async def open_first_product(page):

    print("\n=== Opening the first one product ===")

    await asyncio.sleep(2)

    first_product = page.locator("(//div[contains(@class,'br-pp-ipd-hidden')]//a)[1]")

    url = await first_product.get_attribute("href")
    print("Product URL:", url)

    await first_product.click()

    print("Go to the next page")

    await page.wait_for_selector("//h1[contains(@class, 'desktop-only-title')]")

async def collect_product(page):

    print("\n=== Collecting product ===")

    product_data = {}

    try:
        full_name = await page.locator("//h1[contains(@class, 'desktop-only-title')]").inner_text()
        product_data["full_name"] = full_name
        print(f"Full name: {full_name}")
    except Exception:
        product_data["full_name"] = None
        print("Full name not found")

    try:
        container = page.locator("//div[contains(@class,'product-content-wrapper')]")
        code = await container.get_attribute("data-code")
        product_data["code"] = code
        print(f"Code: {code}")
    except Exception:
        product_data["code"] = None
        print("Code not found")

    url = page.url
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

    try:
        memory = await page.locator("//div[contains(@class, 'current-product-series')]"
                              "//div[contains(@class, 'series-characteristic')]//a"
        ).inner_text()
        product_data["memory"] = memory
        print(f"Memory: {memory}")
    except Exception:
        try:
            memory = await page.locator(
                "//div[contains(@class, 'br-pr-chr-item')]//span[contains(text(), 'Вбудована пам')]"
                "/following-sibling::span//a"
            ).inner_text()
            product_data['memory'] = memory
            print(f"Memory (from characteristics): {memory}")
        except Exception:
            product_data['memory'] = None
            print("Memory not found")

    try:
        main_container = page.locator(
            "//div[contains(@class, 'container') and contains(@class, 'product-content-wrapper')]"
        )
        manufacturer = await main_container.get_attribute('data-vendor')
        product_data['manufacturer'] = manufacturer
        print(f"Manufacturer: {manufacturer}")
    except Exception:
        product_data['manufacturer'] = None
        print("Manufacturer not found")

    try:
        default_price = await page.locator(
            "//div[contains(@class, 'br-pr-op')]//div[contains(@class, 'price-wrapper')]/span"
        ).inner_text()
        default_price = float(default_price.replace(" ", "").replace("₴", ""))
        product_data['default_price'] = default_price
        print(f"Default price: {default_price}")
    except Exception:
        product_data['default_price'] = None
        print("Default price not found")

    try:
        sale_price = await page.locator(
            "//div[contains(@class, 'br-pr-np')]//span[contains(@class, 'red-price')]"
        ).inner_text()
        sale_price = float(sale_price.replace(" ", "").replace("₴", ""))
        product_data['sale_price'] = sale_price
        print(f"Sale price: {sale_price}")
    except Exception:
        try:
            sale_price = await page.locator(
                "//div[contains(@class, 'br-pr-np')]//div[contains(@class, 'price-wrapper')]/span"
            ).inner_text()
            sale_price = float(sale_price.replace(" ", "").replace("₴", ""))
            product_data['sale_price'] = sale_price
            print(f"Sale price: {sale_price}")
        except Exception:
            product_data['sale_price'] = None
            print("Sale price not found")

    try:
        images = []
        image_elements = page.locator(
            "//div[contains(@class, 'br-pr-slider')]//img[contains(@class, 'br-main-img')]"
        )
        count = await image_elements.count()

        for i in range(count):
            src = await image_elements.nth(i).get_attribute("src")
            if src and src.startswith("http") and src not in images:
                images.append(src)

        product_data['images'] = images
        print(f"Photos: {len(images)} found")
    except Exception:
        product_data['images'] = []
        print("Photos not found")

    import re

    try:
        reviews_link = page.locator("//a[contains(@href, '#reviews')]//span")

        reviews_text = (await reviews_link.first.inner_text()).strip()
        reviews_match = re.search(r'(\d+)', reviews_text)
        reviews_count = int(reviews_match.group(1)) if reviews_match else 0
        print(f"Reviews count: {reviews_count}")

        product_data["reviews_count"] = reviews_count


    except Exception as e:
        print(f"Error finding reviews: {e}")
        product_data["reviews_count"] = 0

    display_section = page.locator(
        "//div[contains(@class,'br-pr-chr-item') and .//h3[contains(text(),'Дисплей')]]"
    )

    await display_section.wait_for(state="attached", timeout=5000)

    rows = display_section.locator("xpath=.//div[span]")

    rows_count = await rows.count()

    try:
        for i in range(rows_count):

            row = rows.nth(i)

            spans = row.locator("span")

            if await spans.count() >= 2:

                key = (await spans.nth(0).inner_text()).strip().lower()

                if "діагональ" in key or "diagonal" in key:

                    links = spans.nth(1).locator("a")

                    if await links.count() > 0:
                        product_data["screen_diagonal"] = (
                            await links.nth(0).inner_text()
                        ).strip()
                    else:
                        product_data["screen_diagonal"] = (
                            await spans.nth(1).inner_text()
                        ).strip()

                    print(f"Screen diagonal: {product_data['screen_diagonal']}")
                    break

    except Exception:
        product_data["screen_diagonal"] = None
        print("Screen diagonal not found")

    try:

        for i in range(rows_count):

            row = rows.nth(i)

            spans = row.locator("span")

            if await spans.count() >= 2:

                key = (await spans.nth(0).inner_text()).strip().lower()

                if (
                        "роздільна" in key
                        or "здатність" in key
                        or "resolution" in key
                ):

                    links = spans.nth(1).locator("a")

                    if await links.count() > 0:
                        product_data["display_resolution"] = (
                            await links.nth(0).inner_text()
                        ).strip()
                    else:
                        product_data["display_resolution"] = (
                            await spans.nth(1).inner_text()
                        ).strip()

                    print(
                        f"Display resolution: {product_data['display_resolution']}"
                    )
                    break

    except Exception:
        product_data["display_resolution"] = None
        print("Display resolution not found")

    print("\n--- Collecting characteristics ---")

    characteristics = {}

    try:

        char_blocks = page.locator(
            "//div[contains(@class,'br-pr-chr')]/div[contains(@class,'br-pr-chr-item')]"
        )

        block_count = await char_blocks.count()

        print(f"Found {block_count} characteristic blocks")

        for i in range(block_count):

            block = char_blocks.nth(i)

            try:
                block_title = (
                    await block.locator("xpath=.//h3").inner_text()
                ).strip()
            except Exception:
                block_title = "Загальні"

            rows = block.locator("xpath=.//div[span]")
            row_count = await rows.count()

            for j in range(row_count):

                row = rows.nth(j)

                spans = row.locator("span")

                if await spans.count() >= 2:

                    key = (await spans.nth(0).inner_text()).strip()

                    links = spans.nth(1).locator("a")

                    if await links.count() > 0:

                        values = []

                        link_count = await links.count()

                        for k in range(link_count):

                            text = (await links.nth(k).inner_text()).strip()

                            if text:
                                values.append(text)

                        value = ", ".join(values)

                    else:

                        value = (await spans.nth(1).inner_text()).strip()

                    value = re.sub(r"\s+", " ", value).strip()

                    if key and value and key != value:

                        if block_title != "Загальні":
                            full_key = f"{block_title}: {key}"
                        else:
                            full_key = key

                        characteristics[full_key] = value

        product_data["characteristics"] = characteristics

        print(f"Characteristics collected: {len(characteristics)}")

    except Exception as e:

        product_data["characteristics"] = {}

        print(f"Error collecting characteristics: {e}")

    return product_data

async def print_product_data(product_data):

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


async def save_to_database(product_data):
    """
    Stores collected data in PostgreSQL via Django ORM (async version)
    """
    print("\n--- Saving to Database ---")

    @sync_to_async
    def save_all():

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

        Product_Image.objects.filter(product=product).delete()
        images = product_data.get('images', [])
        for img_url in images:
            Product_Image.objects.create(
                product=product,
                url=img_url
            )

        Product_Characteristics.objects.filter(product=product).delete()
        characteristics = product_data.get('characteristics', {})
        for key, value in characteristics.items():
            Product_Characteristics.objects.create(
                product=product,
                key=key,
                value=value
            )

        return product, created, len(images), len(characteristics)

    product, created, images_count, chars_count = await save_all()

    action = "Created" if created else "Updated"
    print(f"{action} product: {product.full_name}")
    print(f"{images_count} photos are saved")
    print(f"{chars_count} characteristics are saved")
    print("Successfully saved to PostgreSQL!")

    return product

async def main():


    async with async_playwright() as p:

        browser = await p.firefox.launch(headless=False)

        page = await browser.new_page()

        await search_product(page)
        print("Searching product...")

        await open_first_product(page)

        product_data = await collect_product(page)

        await print_product_data(product_data)

        await save_to_database(product_data)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())