# %% imports
from bs4 import BeautifulSoup
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime
# end%%

# %% Old function
def enter_single_search(origin,destination,outbound_date_str,return_date_str,
    method='dollars',driver=None,
    url='https://www.southwest.com/flight/search-flight.html?',
    available_codes=None, wait_time=.2,
    proxies=None):

    if not driver is None:
        logging.warning('you specified a driver...we no longer use selenium, Driver should always be None...continueing')

    payload = {
        'twoWayTrip': True,
        'airTranRedirect': "",
        'returnAirport': "RoundTrip",
        'outboundTimeOfDay': "ANYTIME",
        'returnTimeOfDay': "ANYTIME",
        'seniorPassengerCount': 0,
        'fareType': "DOLLARS",
        'originAirport': origin,
        'destinationAirport': destination,
        'outboundDateString': outbound_date_str,
        'returnDateString': return_date_str,
        'adultPassengerCount': 1}

    verify = get_verify(proxies)
    r =requests.post(url,params=payload,proxies=proxies,verify=verify)

    logging.info('Got payload back from SW')
    return r

# end%%

# %% Paylod with requests
payload = {
    'adultPassengersCount':1,
    'departureDate':'2018-05-16',
    'departureTimeOfDay':'ALL_DAY',
    'destinationAirportCode':'BOI',
    'fareType':'USD',
    'int':'HOMEQBOMAIR',
    'leapfrogRequest':True,
    'originationAirportCode':'ATL',
    'passengerType':'ADULT',
    'promoCode':'',
    'returnAirportCode':'',
    'returnDate':'2018-05-20',
    'returnTimeOfDay':'ALL_DAY',
    'seniorPassengersCount':0,
    'tripType':'roundtrip'}
url="https://www.southwest.com/air/booking/select.html?"
r =requests.post(url,params=payload)

print(r.url)
r.url
with open('super.html', 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)
# with open('output.html',mode='w') as f:
#     f.write(r.text)
# end%%

# # %%
# browser = webdriver.PhantomJS()
#
# browser.get(r.url)
# browser.execute_script("return document.body.innerHTML")
# r.url
# with open('output_sel.html','w') as f:pyth
#     f.write(browser.page_source)
# end%%

# %% Try with chrome
chrome_options = Options()
chrome_options.set_headless(True)
# chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"
browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
browser.get(r.url)
try:
    # Webdriver might be too fast. Tell it to slow down.
    wait = WebDriverWait(browser, 120)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "currency_dollars")))
    print("[%s] Results loaded." % (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
except TimeoutError:
    print("[%s] Results took too long!" % (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
with open('output_chrome.html','w') as f:
    f.write(browser.page_source)
# end%%

r.url
# %%
adultPassengersCount=1
departureDate=2018-05-15
departureTimeOfDay=ALL_DAY
destinationAirportCode=ATL
fareType=USD
originationAirportCode=GSP
passengerType=ADULT
promoCode=
returnAirportCode=
returnDate=2018-05-20
returnTimeOfDay=ALL_DAY
seniorPassengersCount=0
tripType=roundtrip

print(r.url)

# end%%
