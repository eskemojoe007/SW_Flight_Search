import googlemaps
from datetime import datetime
import pandas as pd
gmaps = googlemaps.Client(key='AIzaSyD5342S4ws31btGQCSptFBt_knn8u683do')
datetime.now()


directions_result = gmaps.directions("21 Jones Ave, Greenville, SC",
                                     "ATL",departure_time=datetime(2018,5,3,12)
                                     ,traffic_model ='pessimistic'
                                    )
directions_result[0]
print(directions_result[0]['legs'][0]['distance']['text'])
pd.to_timedelta(directions_result[0]['legs'][0]['duration']['text'].replace('mins','min'))
pd.to_timedelta(directions_result[0]['legs'][0]['duration_in_traffic']['text'].replace('mins','min'))
# https://stackoverflow.com/questions/17267807/python-google-maps-driving-time
