import pprint
import time
import random
import sys
import json

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from bs4 import BeautifulSoup
from datetime import datetime

PROXIES = ['http://user73951:qv0enf@176.56.37.179:3898',
           'http://user73951:qv0enf@176.56.37.205:3898']


def _get_driver():
    my_proxy = random.choice(PROXIES)
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': my_proxy,
        'sslProxy': my_proxy,
        'noProxy': ''})
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.proxy = proxy
    return webdriver.Chrome(options=chrome_options)


def _get_html_page(link: str, count_scroll: int = 8) -> str:
    driver = _get_driver()
    driver.get(link)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.24)
    for i in range(count_scroll):
        driver.execute_script("scrollBy(0,-700);")
        time.sleep(0.3)
    return driver.page_source


def parser(link: str) -> dict:
    try:
        html_page = _get_html_page(link)
        print("Get page")
        parse_data = {"call_time": datetime.now().isoformat(),
                      "link": link}
        soup = BeautifulSoup(html_page, "html.parser")
        body = soup.find('body')
        # print(body.prettify())

        data_with_code = body.findAll("p",
                                      class_="MuiTypography-root MuiTypography-body2 css-a6rvnt")
        parse_data["imo_code"] = int(data_with_code[1].find("b").text)
        print("Get imo_code")

        data_with_departure_code = body.findAll("a",
                                                class_="MuiTypography-root MuiTypography-h5 MuiLink-root MuiLink-underlineHover css-1dwmafv")
        if len(data_with_departure_code) == 1:
            data_with_departure_code = data_with_departure_code[0]
            parse_data["departure_code"] = ''.join(
                p.text for p in data_with_departure_code.findAll("b"))
            parse_data["arrival_code"] = ""
            print("Get ports code")

            parse_data["departure_name"] = body.find("span",
                                                     class_="MuiTypography-root MuiTypography-caption css-1todb2c").text
            parse_data["arrival_name"] = body.find("p",
                                                   class_="MuiTypography-root MuiTypography-body1 css-5fhgm2").text
            print("Get ports name")
        else:
            parse_data["departure_code"] = ''.join(
                p.text for p in data_with_departure_code[0].findAll("b"))
            parse_data["arrival_code"] = ''.join(
                p.text for p in data_with_departure_code[1].findAll("b"))
            print("Get ports code")

            data_with_name = body.findAll("span",
                                          class_="MuiTypography-root MuiTypography-caption css-1todb2c")
            parse_data["departure_name"] = data_with_name[0].text
            parse_data["arrival_name"] = data_with_name[1].text
            print("Get ports name")

        parse_data["draught"] = float(
            body.find("div", id="voyageInfo-section-draught").find("b").text.split()[0])
        print("Get draught")

        data_with_position = body.findAll("p",
                                          class_="MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom css-1f2xc97")
        parse_data["position_received"] = data_with_position[0].find("b").text
        print("Get position received")

        parse_data["speed"] = float(data_with_position[5].find("b").text.split()[0])
        print("Get speed")

        text = body.find("div",
                         class_="MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-2 css-isbt42").find(
            "div", class_="MuiGrid-root MuiGrid-item css-1wxaqej").find("div")["style"]
        parse_data["longitude"], parse_data["latitude"] = map(float, text.split("(")[2].split(")")[
            0].split(","))

        return parse_data
    except Exception as ex:
        print(ex)


def main():
    time_now = datetime.now().isoformat()
    data = []
    links = sys.argv[1:]
    for link in links:
        print("Link now:", link)
        link_data = parser(link)
        while link_data is None:
            print(f"link: {link} failed. Try again after 15 seconds")
            time.sleep(15)
            link_data = parser(link)
        data.append(link_data)
        pprint.pprint(data)

    with open(f'static/{time_now}.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()
