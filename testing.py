# %% Import Libraries
import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
# end%%

# %% Set inputs
url = 'https://www.southwest.com/flight/search-flight.html'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page,'html.parser')

options = soup.find(attrs={'class':'stationInput','id':'originAirport'}).findAll('option')
for option in options:
    print option['value']
# end%%

# %% Broswers
driver = webdriver.Firefox()
driver.get(url)
departure = driver.find_element_by_id('originAirport_displayed')
departure.clear()
departure.send_keys('ATL')
departure.send_keys(Keys.RETURN)

arrival = driver.find_element_by_id('destinationAirport_displayed')
arrival.clear()
arrival.send_keys('GSP')
arrival.send_keys(Keys.RETURN)

outbound_date = driver.find_element_by_id('outboundDate')
outbound_date.clear()
outbound_date.send_keys('12/12/2017')
outbound_date.send_keys(Keys.RETURN)

return_date = driver.find_element_by_id('returnDate')
return_date.clear()
return_date.send_keys('12/30/2017')
return_date.send_keys(Keys.RETURN)

radio = driver.find_element_by_id('dollars')
radio.click()

driver.find_element_by_id('submitButton').click()
# end%%

# %%

soup = BeautifulSoup(driver.page_source,'html.parser')
outbounds = soup.find(attrs={'id':'faresOutbound'}).findAll('tr',{'id': re.compile('outbound_flightRow_.*')})

for outbound in outbounds:

    for price in outbounds.findAll('label',{'class':'product_price'}):
        soup.parent()
# [i.text.strip() for i in outbounds[0].findAll('label',{'class':'product_price'})]

# end%%
