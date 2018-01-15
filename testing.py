# %% Import Libraries
import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates
import seaborn as sns
from matplotlib.dates import HOURLY, DateFormatter, rrulewrapper, RRuleLocator,AutoDateFormatter

sns.set()
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
departure.send_keys(u'Atlanta, GA - ATL')
# departure.send_keys(Keys.RETURN)

arrival = driver.find_element_by_id('destinationAirport_displayed')
arrival.clear()
arrival.send_keys(u'Greenville/Spartanburg, SC - GSP')
# arrival.send_keys(Keys.RETURN)

outbound_date = driver.find_element_by_id('outboundDate')
outbound_date.clear()
outbound_date.send_keys('05/03/2018')
# outbound_date.send_keys(Keys.RETURN)

return_date = driver.find_element_by_id('returnDate')
return_date.clear()
return_date.send_keys('05/07/2018')
# return_date.send_keys(Keys.RETURN)

radio = driver.find_element_by_id('dollars')
radio.click()

driver.find_element_by_id('submitButton').click()
# end%%

# %%

soup = BeautifulSoup(driver.page_source,'html.parser')
outbounds = soup.find(attrs={'id':'faresOutbound'}).findAll('tr',{'id': re.compile('outbound_flightRow_.*')})


df = []
for outbound in outbounds:

    depart_time = pd.to_datetime(
        '12/22/2017' + ' ' +
        outbound.find('td',{'class':'depart_column'}).find('span',{'class':'time'}).text
        + outbound.find('td',{'class':'depart_column'}).find('span',{'class':'indicator'}).text)
    arrive_time = pd.to_datetime(
        '12/22/2017' + ' ' +
        outbound.find('td',{'class':'arrive_column'}).find('span',{'class':'time'}).text
        + outbound.find('td',{'class':'arrive_column'}).find('span',{'class':'indicator'}).text)

    travel_time = pd.to_timedelta(outbound.find('span',{'class':'duration'}).text)

    outbound.find('td',{'class':'routing_column'}).find('span',{'style':'display:none'}).text

    prices = [float(re.sub('\$','',p.text.strip())) for p in outbound.findAll('label',{'class':'product_price'})]
    try:
        price = np.min(prices)
    except ValueError:
        price = np.nan

    df.append({'depart_time':depart_time,'arrive_time':arrive_time,'travel_time':travel_time,'price':price})

df = pd.DataFrame(df)
# end%%

# %%
df['arrive_time_act'] = df['depart_time'] + df['travel_time']
df['agony'] = df['price'] + df['travel_time'].apply(lambda x: x.total_seconds()/3600.*20.0)

df.sort_values('agony',inplace=True)
# end%%

# %% Plot the results
fig, ax = plt.subplots()

starts = dates.date2num(df['depart_time'].tolist())
stops = dates.date2num(df['arrive_time_act'].tolist())


df
ax.barh(range(len(df.index)),stops-starts,0.75,starts)
rule = rrulewrapper(HOURLY, interval=2)
loc = RRuleLocator(rule)
formatter = DateFormatter('%H:%M')
ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(formatter)
labelsx = ax.get_xticklabels()
plt.setp(labelsx, rotation=30,ha='right')
ax.set_yticks(range(len(df.index)))
ax.yaxis.grid(False)
# ax.yaxis.set_visible(False)

for i in df.index:
    ax.text(stops[i]- 10./60/24,i,strfdelta(df['travel_time'].loc[i],'{H}:{M:02}'),va='center',ha='right',color='w')

ax.set_yticklabels(df['price'].apply(lambda x: '$%.0f'%(np.round(x))))
plt.show()
# end%%


# %%
from string import Formatter
from datetime import timedelta

def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

# end%%
