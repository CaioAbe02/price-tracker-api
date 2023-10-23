from bs4 import BeautifulSoup
from requests_html import HTMLSession

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
url = "https://pt.aliexpress.com/item/1005003414304900.html?spm=a2g0o.detail.0.0.58ba7479jyZNfb&gps-id=pcDetailTopMoreOtherSeller&scm=1007.40000.327270.0&scm_id=1007.40000.327270.0&scm-url=1007.40000.327270.0&pvid=1dd14441-fc7b-4abb-88a9-ec782b92e636&_t=gps-id:pcDetailTopMoreOtherSeller,scm-url:1007.40000.327270.0,pvid:1dd14441-fc7b-4abb-88a9-ec782b92e636,tpp_buckets:668%232846%238111%231996&pdp_npi=4%40dis%21BRL%2142.31%2134.28%21%21%218.11%21%21%402103010b16926627913375047ecfb6%2112000025681351568%21rec%21BR%214175224671%21"

session = HTMLSession()

r = session.get(url)

r.html.render()

r.html.html

soup1 = BeautifulSoup(r.html.html, "html.parser")
soup2 = BeautifulSoup(soup1.prettify(), "html.parser")

div = soup2.find('div', class_='product-price-current')
#price_element = div.find_all('span')

print(div)