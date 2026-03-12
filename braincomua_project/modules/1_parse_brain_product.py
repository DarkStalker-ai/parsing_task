
from load_django import *
from parser_app.models import Product, Product_Image, Product_Characteristics
import requests
from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "uk,en-US;q=0.9,en;q=0.8,ru;q=0.7",
    "cache-control": "max-age=0",
    # "cookie": "Lang=ua; CityID=23562; entryRef=Direct; entryPage=%2Fukr%2FMobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html; _gcl_au=1.1.1175841444.1772704164; sc=6B34F579-6DFA-D9AE-8669-C7F0E02044FA; _ga=GA1.1.1682982716.1772704164; _fbp=fb.2.1772704164542.831640394808577242; _clck=1u77kor%5E2%5Eg43%5E0%5E2255; PHPSESSID=gs8jk3p2fq9u8q7nkfr3jfqlis; biatv-cookie={%22firstVisitAt%22:1772704163%2C%22visitsCount%22:1%2C%22currentVisitStartedAt%22:1772704163%2C%22currentVisitLandingPage%22:%22https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html%22%2C%22currentVisitUpdatedAt%22:1772716203%2C%22currentVisitOpenPages%22:3%2C%22campaignTime%22:1772704163%2C%22campaignCount%22:1%2C%22utmDataCurrent%22:{%22utm_source%22:%22(direct)%22%2C%22utm_medium%22:%22(none)%22%2C%22utm_campaign%22:%22(direct)%22%2C%22utm_content%22:%22(not%20set)%22%2C%22utm_term%22:%22(not%20set)%22%2C%22beginning_at%22:1772704163}%2C%22utmDataFirst%22:{%22utm_source%22:%22(direct)%22%2C%22utm_medium%22:%22(none)%22%2C%22utm_campaign%22:%22(direct)%22%2C%22utm_content%22:%22(not%20set)%22%2C%22utm_term%22:%22(not%20set)%22%2C%22beginning_at%22:1772704163}}; _ga_00SJWGYFLM=GS2.1.s1772716204$o4$g1$t1772716240$j24$l0$h1894993895",
    # "priority": "u=0, i",
    "sec-ch-ua": '"Opera GX";v="127", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 OPR/127.0.0.0 (Edition std-2)"
}
url = f'https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html'

product = {
    "full_name": None,
    "color": None,
    "memory": None,
    "manufacturer": None,
    "default_price": None,
    "sale_price": None,
    "code": None,
    "reviews_count": 0,
    "screen_diagonal": None,
    "display_resolution": None,
    "images": [],
    "characteristics": {}
}

try:
    r = requests.get(url, headers=headers, timeout=10)

    soup = BeautifulSoup(r.text, 'html.parser')

    try:
        product["full_name"] = soup.find('h1', class_='main-title').text.strip()
    except AttributeError:
        product["full_name"] = None

    try:
        product["code"] = soup.find('span', class_='br-pr-code-val').text.strip()
    except AttributeError:
        product["code"] = None

    try:
        color_span = soup.find('span', string='Колір')
        if color_span:

            parent = color_span.find_parent('div')
            value_span = parent.find_all('span')[1]
            color_link = value_span.find('a')

            if color_link:
                color_text = color_link.text.strip().lower()
            else:
                color_text = value_span.text.strip().lower()

            if 'чорний' in color_text:
                product["color"] = 'black'
            elif 'пустельний' in color_text:
                product["color"] = 'desert titanium'
            elif 'натуральний' in color_text:
                product["color"] = 'natural titanium'


    except Exception as e:
        print(f"Помилка кольору: {e}")
        product["color"] = None

    try:
        if "256GB" in product["full_name"] or "256 Gb" in product["full_name"]:
            product["memory"] = "256 Gb"
        elif "512GB" in product["full_name"]:
            product["memory"] = "512 Gb"
        elif "1TB" in product["full_name"]:
            product["memory"] = "1 Tb"
    except AttributeError:
        product["memory"] = None

    try:
        container = soup.find('div', class_='container br-container-main br-container-prt product-content-wrapper')
        product["manufacturer"] = container.get('data-vendor')
    except (AttributeError, KeyError):
        try:
            if product["full_name"] and "Apple" in product["full_name"]:
                product["manufacturer"] = "Apple"
        except (TypeError, AttributeError):
            product["manufacturer"] = None

    try:
        price_text = soup.find('div', class_='br-pr-np').find('div', class_='price-wrapper').find('span').text.strip()
        price_text = price_text.replace(" ", "").replace("₴", "")
        if price_text.replace('.', '').isdigit():
            product["default_price"] = float(price_text)
            product["sale_price"] = None
    except (AttributeError, ValueError):
        product["default_price"] = None
        product["sale_price"] = None

    try:
        import re
        review_text = soup.find('a', class_='reviews-count').text.strip()
        numbers = re.findall(r'\d+', review_text)
        if numbers:
            product["reviews_count"] = int(numbers[0])
    except (AttributeError, ValueError):
        product["reviews_count"] = 0

    try:
        diag_elem = soup.find('span', string=re.compile(r'Діагональ екрану'))
        parent = diag_elem.find_parent('div')
        product["screen_diagonal"] = parent.find_all('span')[1].text.strip()
    except AttributeError:
        product["screen_diagonal"] = None

    try:
        res_elem = soup.find('span', string=re.compile(r'Роздільна здатність'))
        parent = res_elem.find_parent('div')
        product["display_resolution"] = parent.find_all('span')[1].text.strip()
    except (AttributeError, IndexError):
        product["display_resolution"] = None

    try:
        images = soup.find_all('img', class_='br-main-img')
        for img in images:
            src = img.get('src')
            if src and src.startswith('http') and src not in product["images"]:
                product["images"].append(src)
    except AttributeError:
        product["images"] = []

    try:
        char_sections = soup.find_all('div', class_='br-pr-chr-item')
        for section in char_sections:
            section_title = section.find('h3')
            section_name = section_title.text.strip() if section_title else "General"

            rows = section.find_all('div', recursive=False)
            for row in rows:
                spans = row.find_all('span')
                if len(spans) >= 2:
                    key = spans[0].text.strip()
                    value = spans[1].text.strip()
                    full_key = f"{section_name}: {key}"
                    product["characteristics"][full_key] = value
    except AttributeError:
        product["characteristics"] = {}


except requests.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

def save_product(data):
    try:
        product_obj, created = Product.objects.update_or_create(
            code=data["code"],
            defaults={
                "full_name": data["full_name"],
                "color": data["color"],
                "memory": data["memory"],
                "manufacturer": data["manufacturer"],
                "default_price": data["default_price"],
                "sale_price": data["sale_price"],
                "reviews_count": data["reviews_count"],
                "screen_diagonal": data["screen_diagonal"],
                "display_resolution": data["display_resolution"],
            }
        )

        for img_url in data.get("images", []):
            Product_Image.objects.get_or_create(
                product=product_obj,
                url=img_url
            )

        for key, value in data.get("characteristics", {}).items():
            Product_Characteristics.objects.get_or_create(
                product=product_obj,
                key=key,
                defaults={"value": value}
            )

        return product_obj

    except Exception as e:
        print(f"Save error to DB: {e}")
        return None



print("\n" + "=" * 40)
print("DATA:")
print("=" * 40)

for key, value in product.items():
    if key in ["images", "characteristics"]:
        print(f"{key}: {len(value)} items")
    else:
        print(f"{key}: {value}")

print("=" * 40)

if product.get("code"):
    print("\nSaving to DB...")
    saved_product = save_product(product)
    if saved_product:
        print("Successfully saved!")
    else:
        print("Failed to save!")
