# %% Imports
import requests
from colored_logger import customLogger
from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import numpy as np
import pytz
import googlemaps
logger = customLogger('SWFLights')
# end%%

# %% define base class with proxy support
class proxy_support(object):
    proxy = None
    verify = None
    def __init__(self):
        pass

    def set_proxy(self,http_proxy,https_proxy=None,verify=None):
        if https_proxy is None:
            https_proxy = http_proxy

        self.proxy = {'http': http_proxy, 'https': https_proxy}
        self.verify = verify

# end%%

# %% Airport Details Class Definition
class AirportDetails(proxy_support):

    def __init__(self,fn='airports.dat'):
        self.fn = fn
        self.get_sw_airports()
        self.get_airport_df()

    def get_sw_airports(self,url='https://www.southwest.com/flight/search-flight.html'):

        logger.debug('Getting available airport codes from SW website')

        r = requests.get(url,proxies=self.proxy,verify=self.verify)

        soup = BeautifulSoup(r.content,'html.parser')

        options = soup.find(attrs={'class':'stationInput','id':'originAirport'}).findAll('option')

        airport_codes = {}
        for option in options:
            airport_codes[option['value']] = option.text

        self.sw_dict = airport_codes

    def _get_airports_dat(self,fn=None,url='https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat'):
        if fn is None:
            fn = self.fn

        if not os.path.isfile(fn):
            logger.info('Could not find the %s file...downloading from github and saving'%(fn))
            r = requests.get(url,proxies=self.proxy,verify=self.verify)
            with codecs.open(fn,'w',encoding=r.encoding) as f:
                f.write(r.text)
        else:
            logger.debug('Found %s...'%(fn))

    def get_airport_df(self,fn=None):

        if fn is None:
            fn = self.fn

        self._get_airports_dat(fn)

        logger.debug('Converting %s to a dataframe of useful information'%(fn))
        self.airport_df = pd.read_csv(fn,index_col=0,
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

    def check_codes(self,codes):
        # This function checks codes against the various airports lists
        # to make sure they are good codes...it has some sub functions

        #Check a singular code if is a SW airport
        def check_code(code,keys):
            if not code.upper() in self.sw_dict.keys():
                bad_code(code.upper())

        #if a bad code is found...then we check in the IATA list
        def bad_code(code):
            logger.warning('Code specified was not found in SW available airports: %s',code)
            if len(self.airport_df.loc[self.airport_df['IATA']==code.upper()]) == 1:
                logger.info('%s Code found in IATA airport list: %s'%(code,self.airport_df['Name'].loc[self.airport_df['IATA']==code.upper()].get_values()[0]))
            else:
                logger.error('Code specified was not found in any IATA airport code list: %s'%code)

            raise ValueError('See logger output')

        # We can take lists of strings, or individual strings here...if we have Anything
        #other than strings...throw an error
        if isinstance(codes, str):
            check_code(codes,self.sw_dict.keys())
        elif all(isinstance(item, str) for item in codes):
            for code in codes:
                check_code(code,self.sw_dict.keys())
        else:
            logger.error('checking airport codes must have all strings')
            raise TypeError('see logger error')

    def get_index(self,airport_code,key_type='IATA'):
        # This function returns the index for a looked up airport code from the
        #IATA data.  It has some error checking

        mask = self.airport_df[key_type].str.upper().str.strip() == airport_code.upper().strip()

        if mask.sum() < 1:
            raise ValueError('Could not find %s in %s data'%(airport_code,key_type))
        elif mask.sum() > 1:
            raise ValueError('Multiple Found of %s in %s data'%(airport_code, key_type))
        else:
            return self.airport_df.index[mask][0]

    def get_timezone_code(self,airport_code,key_type='IATA'):
        # Gets the timezone string from the file
        index = self.get_index(airport_code,key_type=key_type)
        return self.airport_df.at[index,'Tz database time zone']

    def get_lat_long_tup(self,airport_code,key_type='IATA'):

        index = self.get_index(airport_code,key_type=key_type)
        return self.airport_df.at[index,'Latitude'],self.airport_df.at[index,'Longitude']

    def get_lat_long_str(self,airport_code,key_type='IATA'):

        return self._tuple2str(self.get_lat_long_tup(airport_code,key_type=key_type))

    def _tuple2str(self,tup):
        if isinstance(tup,str):
            return tup
        else:
            return "{}".format(','.join(str(ll) for ll in tup))

# end%%

# %% DRIVE TIMES
# gmaps = googlemaps.Client(key='AIzaSyD5342S4ws31btGQCSptFBt_knn8u683do')

def generic_drive_times(origin, destination,gmaps,arrive_time = None, depart_time=None,traffic_model='best_guess'):

    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving")
    initial_drive_time = pd.to_timedelta(
        directions_result[0]['legs'][0]['duration']['text'].replace('mins','min'))



    if (arrive_time is None) and (depart_time is None):
        logger.warning('You didnt specify a time...using generic')
        return initial_drive_time
    elif (not arrive_time is None) and (not depart_time is None):
        logger.error('You specified both...dont know what to do')
        raise ValueError('See Logger Output')
    elif depart_time is None:
        #Specified the arrival time
        depart_time = arrive_time - initial_drive_time
    elif arrive_time is None:
        pass
    else:
        raise ValueError('You have to specify something')

    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         departure_time=depart_time,
                                         traffic_model =traffic_model
                                        )
    return pd.to_timedelta(
        directions_result[0]['legs'][0]['duration_in_traffic']['text'].replace('mins','min'))


# end%%

# %% Single Flight Class Definition
class SWSearch(proxy_support):
    def __init__(self,origin,destination,travel_date,airports=None,method='DOLLARS'):

        if airports is None:
            airports = AirportDetails()
        self.airports = airports

        self.airports.check_codes([origin,destination])

        self.origin = origin.upper()
        self.destination = destination.upper()

        if isinstance(travel_date,str):
            self.outbound_date = pd.to_datetime(travel_date)
            self.outbound_date_str = self.outbound_date.strftime('%m/%d/%Y')
        else:
            logger.warning('Code not set up for non string inputs yet')

        self._check_method(method)
        self.method=method.upper()

    def _check_method(self,method):
        if not ((method.upper() == 'DOLLARS') or (method.upper()=='POINTS')):
            logger.error('method was badly specified...%s please change'%(method.upper()))
            raise ValueError('see logger output')

    def get_single_search(self,
        url='https://www.southwest.com/flight/search-flight.html?'):

        logger.debug('Setting payload')
        payload = {
            'twoWayTrip': False,
            'airTranRedirect': "",
            'outboundTimeOfDay': "ANYTIME",
            'returnTimeOfDay': "ANYTIME",
            'seniorPassengerCount': 0,
            'fareType': self.method,
            'originAirport': self.origin,
            'destinationAirport': self.destination,
            'outboundDateString': self.outbound_date_str,
            'adultPassengerCount': 1}

        r = requests.post(url,params=payload,proxies=self.proxy,verify=self.verify)

        logger.info('Got payload back from SW')
        self.soup = BeautifulSoup(r.content,'html.parser')

    def get_flight_info(self):
        logger.debug('Getting Flight Info')
        table_id = 'faresOutbound'
        re_str = 'outbound_flightRow_.*'
        direction = 'outbound'
        # logger.info('Flights for %s to %s on %s'%(self.origin,self.destination,self.outbound_date_str))
        flights = self.soup.find(attrs={'id':table_id}).findAll('tr',{'id': re.compile(re_str)})
        df = []

        for flight in flights:
            depart_time = pd.to_datetime(
                self.outbound_date_str + ' ' +
                flight.find('td',{'class':'depart_column'}).find('span',{'class':'time'}).text
                + flight.find('td',{'class':'depart_column'}).find('span',{'class':'indicator'}).text)
            arrive_time = pd.to_datetime(
                self.outbound_date_str + ' ' +
                flight.find('td',{'class':'arrive_column'}).find('span',{'class':'time'}).text
                + flight.find('td',{'class':'arrive_column'}).find('span',{'class':'indicator'}).text)

            travel_time = pd.to_timedelta(flight.find('span',{'class':'duration'}).text)

            # flight.find('td',{'class':'routing_column'}).find('span',{'style':'display:none'}).text

            prices = [float(re.sub('\$','',p.text.strip())) for p in flight.findAll('label',{'class':'product_price'})]
            try:
                price = np.min(prices)
            except ValueError:
                price = np.nan

            logger.info('Flight: Depart time %s, Arrival Time %s, Travel Time: %s, Price %s'%(depart_time,arrive_time,travel_time,price))

            df.append({'depart_time':depart_time,'arrive_time':arrive_time,
            'travel_time':travel_time,'price':price,'origin':self.origin,
            'destination':self.destination})

        self.flights = pd.DataFrame(df)
        #
        # return pd.DataFrame(df)

    def correct_flight_info(self):
        # Look up timezones
        tz_origin = self.airports.get_timezone_code(self.origin)
        tz_destination = self.airports.get_timezone_code(self.destination)

        # Use apply functions to add the right timezones
        self.flights['depart_time'] = self.flights['depart_time'].apply(
            lambda x: pytz.timezone(tz_origin).localize(x))

        # Due to after midnight issues...we now use travel time and departure time to replace
        # the read arrive_time
        self.flights['arrive_time'] = (self.flights['depart_time'] + self.flights['travel_time']).apply(
            lambda x: x.astimezone(tz_destination))

    def add_drivetimes(self,start_address,end_address):

        #For now we assume buffer times...these will likely need to change
        depart_buffer = '2 hours'
        arrive_buffer = '30 min'

        self.flights['drive_time_depart'] = self.flights.apply(
            lambda x: generic_drive_times(
            start_address,self.airports.get_lat_long_str(self.origin),gmaps,
            arrive_time=x['depart_time'] - pd.to_timedelta(depart_buffer)
        ),axis=1)

        self.flights['drive_depart_time'] = (self.flights['depart_time']  -
            pd.to_timedelta(depart_buffer) - self.flights['drive_time_depart'])


        self.flights['drive_time_arrive'] = self.flights.apply(
            lambda x: generic_drive_times(
            self.airports.get_lat_long_str(self.destination),end_address,gmaps,
            depart_time=x['arrive_time'] + pd.to_timedelta(arrive_buffer)
        ),axis=1)

        self.flights['drive_arrive_time'] = (self.flights['arrive_time']  -
            pd.to_timedelta(arrive_buffer) - self.flights['drive_time_arrive'])

    def fix_col_order(self):
        self.flights = self.flights[[
        'agony','price','drive_depart_time','drive_time_depart','origin','depart_time',
        'travel_time','arrive_time','destination','drive_time_arrive','drive_arrive_time',
        ]]

        self.flights.sort_values('agony',inplace=True)
    def agony_score(self):
        self.flights['agony'] = (self.flights['price'] +
            self.flights['travel_time'].apply(lambda x: x.total_seconds()/3600.*20.0) +
            self.flights['drive_time_depart'].apply(lambda x: x.total_seconds()/3600.*40.0) +
            self.flights['drive_time_arrive'].apply(lambda x: x.total_seconds()/3600.*40.0))

# end%%

# %%
airport = AirportDetails()
# airport.check_codes(['SLC','BOI','CDG'])
airport.check_codes(['SLC','BOI'])
# airport.check_codes('cdg')

# airport.get_lat_long_str('CDG')
gmaps = googlemaps.Client(key='AIzaSyD5342S4ws31btGQCSptFBt_knn8u683do')
#
# len(airport.airport_df.loc[airport.airport_df['IATA'] == 'CDG'].index)
# 'CDG' in airport.airport_df['IATA']
# airport.airport_df.get_v
# airport.airport_df['Name'].loc[airport.airport_df['IATA'] == 'CDG'].get_values()[0]
# airport.airpot_df['SW Descrip'] = airport.airpot_df['IATA'].map(airport.sw_dict)
# airport.airpot_df.loc[airport.airpot_df['SW Descrip'].dropna()]
# airport.airpot_df.columns
# r = requests.get('https://www.southwest.com/flight/search-flight.html?')
# soup = BeautifulSoup(r.content,'html.parser')
#
# soup.find('form',{'method':'POST','id':'buildItineraryForm'}).findAll('select')

obj = SWSearch('ATL','SLC','3/30/18',airports=airport)
obj.get_single_search()
obj.get_flight_info()
obj.correct_flight_info()

obj.add_drivetimes('21 Jones Ave, Greenville, SC','Worchester Drive, SLC, UT')
obj.agony_score()
obj.fix_col_order()
obj2 = SWSearch('CLT','SLC','3/30/18',airports=airport)
obj2.get_single_search()
obj2.get_flight_info()
obj2.correct_flight_info()

obj2.add_drivetimes('21 Jones Ave, Greenville, SC','Worchester Drive, SLC, UT')
obj2.agony_score()
obj2.fix_col_order()

pd.concat([obj.flights,obj2.flights])

# with open('output.html',mode='w') as f:
#     f.write(r.text)

# end%%
