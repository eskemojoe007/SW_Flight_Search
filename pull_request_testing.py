# %% Import Base Packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
# end%%

# %%
url = 'https://duckduckgo.com/'
payload = {'q':'python'}
r = requests.get(url, params=payload)
print(r.content)
# with open("requests_results.html", "w") as f:
#     f.write(r.content)
# end%%

# %%
# const fetch = () => {
#   osmosis
#     .get("https://www.southwest.com")
#     .submit(".booking-form--form", {
#       twoWayTrip: true,
#       airTranRedirect: "",
#       returnAirport: "RoundTrip",
#       outboundTimeOfDay: "ANYTIME",
#       returnTimeOfDay: "ANYTIME",
#       seniorPassengerCount: 0,
#       fareType: "DOLLARS",
#       originAirport,
#       destinationAirport,
#       outboundDateString,
#       returnDateString,
#       adultPassengerCount
#     })
# end%%

# %%
url = 'https://www.southwest.com/flight/search-flight.html?'
payload = {
    'twoWayTrip': True,
    'airTranRedirect': "",
    'returnAirport': "RoundTrip",
    'outboundTimeOfDay': "ANYTIME",
    'returnTimeOfDay': "ANYTIME",
    'seniorPassengerCount': 0,
    'fareType': "DOLLARS",
    'originAirport': 'GSP',
    'destinationAirport': 'DAL',
    'outboundDateString': '01/17/2018',
    'returnDateString': '01/21/2018',
    'adultPassengerCount': 1}

r =requests.post(url,params=payload)

with open('output.html','w') as f:
    f.write(r.text)
soup = BeautifulSoup(r.text,'lxml')

soup
# end%%

# %% read a row in the table
def read_row(table_soup,rowname):
    row_soup = table_soup.find(rowname)

    #Get the departure time:
    row_soup.find('td',attrs={'class':'depart column'})



# end%%






# %%
faresOutbound = soup.find(attrs={'id':'faresOutbound'})

faresOutbound.findAll(attrs={'class':'product_price'})

with open('faresOutbound.html','w') as f:
    f.write(str(faresOutbound))
type(soup.find(attrs={'id':'faresOutbound'}))
pd.read_html(str(faresOutbound))
soup.find(attrs={'id':'faresOutbound'}).findAll(attrs={'class':'product_price'})
soup.findAll(attrs={'class':'product_price'})

# end%%
