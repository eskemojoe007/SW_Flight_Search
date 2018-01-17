# %% Import Libraries
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import numpy as np
import itertools
import googlemaps
from datetime import datetime
import googlemaps
from matplotlib import pyplot as plt
from matplotlib import dates
import seaborn as sns
from matplotlib.dates import HOURLY, DateFormatter, rrulewrapper, RRuleLocator,AutoDateFormatter, HourLocator
import time
import requests
import os
import codecs
sns.set()
# end%%

# %%
def get_airport_codes(request_obj=None,url='https://www.southwest.com/flight/search-flight.html'):
    if request_obj is None:
        request_obj = requests.get(url)
        # request_obj = urllib3.urlopen(url)

    soup = BeautifulSoup(request_obj.content,'html.parser')

    options = soup.find(attrs={'class':'stationInput','id':'originAirport'}).findAll('option')

    airport_codes = {}
    for option in options:
        airport_codes[option['value']] = option.text

    return airport_codes


def get_airports_dat(fn='airports.dat'):

    if not os.path.isfile(fn):
        response = requests.get('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat')
        with codecs.open(fn,'w',encoding=response.encoding) as f:
            f.write(response.text)

def get_airport_df(fn='airports.dat'):
    get_airports_dat(fn=fn)
    df = pd.read_csv(fn,index_col=0,
        names=['Airport ID',
        'Name',
        'City',
        'Country',
        'IATA',
        'ICAO',
        'Latitude',
        'Longitude',
        'Altitude',
        'Timezone',
        'DST',
        'Tz database time zone',
        'Type',
        'Source'], na_values=['\\N'])
    return df


def check_codes(codes,available_codes=None):
    if available_codes is None:
        available_codes = get_airport_codes().keys()
    if '__iter__' in dir(codes):
        for code in codes:
            if not code.upper() in available_codes:
                raise ValueError('Entered code %s is not valid'%code)
    else:
        if not codes.upper() in available_codes:
            raise ValueError('Entered airport code "%s" is not valid'%codes)
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

# %%
def get_driver(method='Firefox'):
    if method.lower() == 'firefox':
            return webdriver.Firefox()
    else:
        raise ValueError('Invalid entry for get_driver method')
def enter_single_search(origin,destination,outbound_date_str,return_date_str,
    method='dollars',driver=None,
    url='https://www.southwest.com/flight/search-flight.html?',
    available_codes=None, wait_time=.2):

    if not driver is None:
        print('Warning...you specified a driver...we no longer use selenium')

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

    r =requests.post(url,params=payload)

    return r


# def enter_single_search(origin,destination,outbound_date_str,return_date_str,
#     method='dollars',driver=None,
#     url='https://www.southwest.com/flight/search-flight.html',
#     available_codes=None, wait_time=.2):
#
#     if available_codes is None:
#         available_codes = get_airport_codes(url=url)
#     # Check the codes to make sure they are valid
#     check_codes([origin,destination],available_codes=available_codes.keys())
#
#     #check date format - Not doing for now...should use datetime to make it right
#
#     #check driver
#     if driver is None:
#         driver = get_driver()
#
#
#     #Perform the action
#     driver.get(url)
#     departure = driver.find_element_by_id('originAirport_displayed')
#     departure.clear()
#     arrival = driver.find_element_by_id('destinationAirport_displayed')
#     arrival.clear()
#     outbound_date = driver.find_element_by_id('outboundDate')
#     outbound_date.clear()
#     return_date = driver.find_element_by_id('returnDate')
#     return_date.clear()
#
#     time.sleep(wait_time)
#
#
#     departure.send_keys(available_codes[origin.upper()])
#     # departure.send_keys(origin.upper())
#     # departure.send_keys(Keys.RETURN)
#     time.sleep(wait_time)
#     arrival.send_keys(available_codes[destination.upper()])
#     # arrival.send_keys(destination.upper())
#     # arrival.send_keys(Keys.RETURN)
#     time.sleep(wait_time)
#     outbound_date.clear()
#     outbound_date.send_keys(outbound_date_str)
#     time.sleep(wait_time)
#
#     # outbound_date.send_keys(Keys.RETURN)
#     return_date.clear()
#     return_date.send_keys(return_date_str)
#     time.sleep(wait_time)
#     # return_date.send_keys(Keys.RETURN)
#     time.sleep(wait_time)
#     if method.lower() == 'dollars':
#         radio = driver.find_element_by_id('dollars')
#         radio.click()
#     else:
#         raise ValueError('Invalid search method: %s'%method)
#     driver.find_element_by_id('submitButton').click()

def get_results_soup(driver):
    return BeautifulSoup(driver.page_source,'html.parser')

def get_results_soup_request(r):
    return BeautifulSoup(r.content,'html.parser')

def get_outbound_df(soup,date_str,origin,destination):
    outbounds = soup.find(attrs={'id':'faresOutbound'}).findAll('tr',{'id': re.compile('outbound_flightRow_.*')})
    df = []

    for outbound in outbounds:
        depart_time = pd.to_datetime(
            date_str + ' ' +
            outbound.find('td',{'class':'depart_column'}).find('span',{'class':'time'}).text
            + outbound.find('td',{'class':'depart_column'}).find('span',{'class':'indicator'}).text)
        arrive_time = pd.to_datetime(
            date_str + ' ' +
            outbound.find('td',{'class':'arrive_column'}).find('span',{'class':'time'}).text
            + outbound.find('td',{'class':'arrive_column'}).find('span',{'class':'indicator'}).text)

        travel_time = pd.to_timedelta(outbound.find('span',{'class':'duration'}).text)

        outbound.find('td',{'class':'routing_column'}).find('span',{'style':'display:none'}).text

        prices = [float(re.sub('\$','',p.text.strip())) for p in outbound.findAll('label',{'class':'product_price'})]
        try:
            price = np.min(prices)
        except ValueError:
            price = np.nan

        df.append({'depart_time':depart_time,'arrive_time':arrive_time,
        'travel_time':travel_time,'price':price,'origin':origin,
        'destination':destination,'direction':'outbound'})

    return pd.DataFrame(df)
# end%%

# %%
gmaps = googlemaps.Client(key='AIzaSyD5342S4ws31btGQCSptFBt_knn8u683do')

def get_times(origin, destination, arrival_time,traffic_model='best_guess'):
    origin = get_lat_long_string(origin)
    destination = get_lat_long_string(destination)


    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         avoid="ferries")

    departure_time = arrival_time - pd.to_timedelta(directions_result[0]['legs'][0]['duration']['text'].replace('mins','min'))

    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         avoid="ferries",
                                         departure_time=departure_time,
                                         traffic_model =traffic_model
                                        )
    return pd.to_timedelta(directions_result[0]['legs'][0]['duration_in_traffic']['text'].replace('mins','min'))

def get_airport_lookup_index(airport_code,airport_df=None,key_type='IATA'):
    if airport_df is None:
        airport_df = get_airport_df()

    mask = airport_df[key_type].str.upper().str.strip() == airport_code.upper().strip()

    if mask.sum() < 1:
        raise ValueError('Could not find %s in airport df'%(airport_code))
    elif mask.sum() > 1:
        raise ValueError('Multiple Found of %s in airport df'%(airport_code))
    else:
        return airport_df.index[mask][0]

def get_lat_long(airport_code,airport_df=None,key_type='IATA'):
    if airport_df is None:
        airport_df = get_airport_df()

    index = get_airport_lookup_index(airport_code,airport_df=airport_df,key_type=key_type)
    return airport_df.at[index,'Latitude'],airport_df.at[index,'Longitude']

def get_timezone_code(airport_code,airport_df=None,key_type='IATA'):
    if airport_df is None:
        airport_df = get_airport_df()

    index = get_airport_lookup_index(airport_code,airport_df=airport_df,key_type=key_type)

    return airport_df.at[index,'Tz database time zone']

def get_lat_long_string(lat_long_tup):
    if isinstance(lat_long_tup,str):
        return lat_long_tup
    else:
        return "{}".format(','.join(str(ll) for ll in lat_long_tup))



# def get_lat_long(location):
#     geocode = gmaps.geocode(location)
#     return '%.10f, %.10f'%(geocode[0]['geometry']['location']['lat'],geocode[0]['geometry']['location']['lng'])
#
#
# def get_timezone_code(location):
#     lat_long = get_lat_long(location)
#     return gmaps.timezone(location=lat_long,timestamp=datetime.now())['timeZoneId']
# end%%

# %% Get and sort agony
def add_timezones(df,location_key,time_key):
    for city in df[location_key].unique():
        tz_code = get_timezone_code(city)
        df.loc[df[location_key] == city, time_key] = pd.Index(df[time_key].loc[df[location_key] == city].values).tz_localize(tz_code)

    df[time_key] = pd.to_datetime(df[time_key])

def add_drivetimes(df,location_key,time_key,name_key,offset='2 hours',start='21 Jones Ave, Greenville, SC'):
    df[name_key] = df.apply(lambda x: get_times(start,x[location_key],(x[time_key] - pd.to_timedelta(offset)).to_pydatetime()),axis=1)
    df[name_key + '_stamp'] = df[time_key] - pd.to_timedelta(offset) - df[name_key]

def get_sort_agony(df):
    # df['arrive_time'] = pd.Index(df['arrive_time'].values).tz_localize(get_timezone_code('ATL'))
    df['arrive_time_act'] = df['depart_time'] + df['travel_time']
    df['agony'] = (df['price'] + df['travel_time'].apply(lambda x: x.total_seconds()/3600.*20.0) +
        df['depart_drive_time'].apply(lambda x: x.total_seconds()/3600.*40.0))

    return df.sort_values('agony')

# end%%

# %% Do it allows
def do_all_single_flight(origin,destination,outbound_date_str,return_date_str):
    available_dict = get_airport_codes()
    # d = get_driver()
    # enter_single_search(origin,destination,outbound_date_str,return_date_str,driver=d,available_codes=available_dict)
    r = enter_single_search(origin,destination,outbound_date_str,return_date_str,available_codes=available_dict)
    soup = get_results_soup_request(r)
    df = get_outbound_df(soup,outbound_date_str,origin,destination)
    add_timezones(df,'origin','depart_time')
    add_timezones(df,'destination','arrive_time')
    add_drivetimes(df,'origin','depart_time','depart_drive_time')
    return get_sort_agony(df)
# end%%

# %% Do it all multiple
def do_all_multiple_flight(origins,destinations,outbound_date_strs,return_date_strs):
    iters = get_iter_items(origins,destinations,outbound_date_strs,return_date_strs)

    available_dict = get_airport_codes()
    d = get_driver()
    dfs = []
    for i in iters:
        origin = i[0]
        destination = i[1]
        outbound_date_str = i[2]
        return_date_str = i[3]
        enter_single_search(origin,destination,outbound_date_str,return_date_str,driver=d,available_codes=available_dict)
        soup = get_results_soup_request(d)
        df_temp = get_outbound_df(soup,outbound_date_str,origin,destination)
        add_timezones(df_temp,'origin','depart_time')
        add_timezones(df_temp,'destination','arrive_time')
        add_drivetimes(df_temp,'origin','depart_time','depart_drive_time')

        dfs.append(df_temp)
    return dfs

# end%%

# %% get_iter_items
def get_iter_items(origins,destinations,outbound_date_strs,return_date_strs):
    s = [origins,destinations,outbound_date_strs,return_date_strs]
    return list(itertools.product(*s))
# end%%

# %% Testing single flight line by line
available_dict = get_airport_codes()
# d = get_driver()
# enter_single_search(origin,destination,outbound_date_str,return_date_str,driver=d,available_codes=available_dict)
r = enter_single_search('CLT','SLC','05/03/2018','05/07/2018',available_codes=available_dict)
r.text
soup = get_results_soup_request(r)
soup
df = get_outbound_df(soup,'05/03/2018','CLT','SLC')
df
add_timezones(df,'origin','depart_time')
add_timezones(df,'destination','arrive_time')
add_drivetimes(df,'origin','depart_time','depart_drive_time')
df
# end%%
# %%
# enter_single_search('ATL','SLC','05/03/2018','05/07/2018',driver=d,available_codes=available_dict)
df = do_all_single_flight('CLT','SLC','05/03/2018','05/07/2018')
# df
dfs = do_all_multiple_flight(['ATL','CLT'],['SLC'],['05/03/2018','05/04/2018'],['05/07/2018'])
# iters = get_iter_items(['ATL','CLT'],['SLC'],['05/03/2018'],['05/07/2018'])
df = pd.concat(dfs,axis=0).reset_index()
# iters[0][0]
df = get_sort_agony(df)
df
# end%%

# %% Plot some shit
fig, ax = plt.subplots(figsize=(20,12))

starts = dates.date2num(df['depart_time'].tolist()) - 4./24
stops = dates.date2num(df['arrive_time_act'].tolist()) - 4./24

drive_starts = dates.date2num(df['depart_drive_time_stamp'].tolist()) - 4./24
drive_stops = dates.date2num((df['depart_drive_time_stamp'] + df['depart_drive_time']).tolist()) - 4./24

ax.barh(range(len(df.index)),stops-starts,0.75,starts)
ax.barh(range(len(df.index)),drive_stops-drive_starts,0.75,drive_starts)
# rule = rrulewrapper(HOURLY, interval=2, byhour=1)
# loc = RRuleLocator(rule)
formatter = DateFormatter('%H')
ax.xaxis.set_major_locator(HourLocator(interval=2))
ax.xaxis.set_major_formatter(formatter)
labelsx = ax.get_xticklabels()
plt.setp(labelsx, rotation=30,ha='right')
ax.set_yticks(range(len(df.index)))
ax.yaxis.grid(False)
# ax.yaxis.set_visible(False)
df
for n, i in enumerate(df.index):
    ax.text((stops[n]- starts[n])/2 + starts[n] ,n,strfdelta(df['travel_time'].loc[i],'{H}:{M:02}'),va='center',ha='center',color='w')
    ax.text(starts[n]+ 10./60/24,n,df['origin'].loc[i],va='center',ha='left',color='w')
    ax.text(stops[n]- 10./60/24,n,df['destination'].loc[i],va='center',ha='right',color='w')

ax.set_yticklabels(df['price'].apply(lambda x: '$%.0f'%(np.round(x))))
plt.show()
# end%%

# %% copy and Play
df_new = df.copy()
df_new.columns.values

df_new
# end%%
