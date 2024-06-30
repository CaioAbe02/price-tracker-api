from datetime import date
import requests
from bs4 import BeautifulSoup

PRICE_ERROR = "PRICE_ERROR"
PRODUCT_UNAVAILABLE = "PRODUCT_UNAVAILABLE"

def get_product_price(url):
   price = None
   price_element = None
   store = get_store(url)
   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
   page = requests.get(url, headers=headers)
   soup1 = BeautifulSoup(page.content, "html.parser")
   soup2 = BeautifulSoup(soup1.prettify(), "html.parser")

   if store == "amazon":
      for i in range(100):
         page = requests.get(url, headers=headers)
         soup1 = BeautifulSoup(page.content, "html.parser")
         soup2 = BeautifulSoup(soup1.prettify(), "html.parser")

         if (soup2.find('div', id='outOfStock') is not None):
            return PRODUCT_UNAVAILABLE

         price_element = soup2.find('span', class_='a-offscreen')
         if price_element is not None:
            break
      if price_element is None:
         return PRICE_ERROR
   elif store == "kabum":
      price_element = soup2.find('h4', class_='finalPrice')
   elif store == "mercadolivre":
      div = soup2.find('div', class_='ui-pdp-price__second-line')

      if div is not None:
         price_element = div.find('span', class_='andes-money-amount__fraction')
         price_cents = div.find('span', class_='andes-money-amount__cents')

   if price_element is not None:
      price = price_element.text.replace("R$", "")

      if store == "mercadolivre" and price_cents is not None:
         price_cents = price_cents.text.strip()
         price = f"{price.strip()},{price_cents}"

   else:
      return PRODUCT_UNAVAILABLE

   if "." in price:
      price = price.replace(".", "")

   return float(price.replace(",", ".").strip())

def get_store(url):
   if "amazon" in url.strip("."):
      return "amazon"
   elif "kabum" in url.strip("."):
      return "kabum"
   elif "mercadolivre" in url.strip("."):
      return "mercadolivre"
   return None

def get_current_date():
   return date.today().strftime("%d/%m/%Y")