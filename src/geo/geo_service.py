import geopandas
import requests
import json
from shapely.geometry import Point
import dotenv 
import numpy as np
from src.server_config.config import Config
import os
from src.server_config.service.cache import Cache
class GeoService:
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance  = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._init :
            return
        self.cities = None
        self.cache = Cache()
        self.config = Config()
        self._init_spatial_inx()
        dotenv.load_dotenv(self.config.env_path)
    
    def _init_spatial_inx(self):
        try:
            print('Loading geopandas....... (Do not close)')
            self.cities = geopandas.read_file('src/assets/geo/geoBoundariesCGAZ_ADM1.geojson')
            self.sindex = self.cities.sindex
            print('Don')
        except Exception as e:
            raise e
    

        
    def get_city_from_point(self,longitude:float,latitude:float, posible_indx:list = None):
        """get city
        if cache is true and indexes, loop throught the possible cities base on indexes
        but if not found in cache, recursive with out cache and list of indexes 
        if cache is false or indexes not pass, we get the possible cities from spial indexes

        Args:
            longitude (): _description_
            latitude (float): _description_
            cache (bool, optional): _description_. Defaults to False.
            posible_indx (list, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        point = Point(longitude,latitude)
        if posible_indx is None:
            posible_indx = list(self.sindex.intersection(point.bounds))
        posible_cities = self.cities.iloc[posible_indx]
        
        for _,city in posible_cities.iterrows():
            if city.geometry.contains(point):
                return city['shapeName'], posible_indx
       
        return None, None            
    
             
    
    
    def get_tempature(self,longitude:float,latitude:float):
        """return tempature

        Args:
            longitude (float): _description_
            latitude (float): _description_

        Returns:
            _type_: _description_
        """
        url =f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m'
        respond = requests.get(url=url)
        if respond.status_code !=200:
            return None
        
        data= respond.json() 
        print('data',data)
        return data['current']['temperature_2m']
    def get_aqi(self,longitude:float,latitude:float):
        """
        return aqi
        
        :param self: Description
        :param longitude: Description
        :type longitude: float
        :param latitude: Description
        :type latitude: float
        :return: Description
        :rtype: Any
        """ 
        token = os.getenv('AQI_API_KEY')
        url =f'https://api.waqi.info/feed/geo:{latitude};{longitude}/?token={token}'
        respond = requests.get(url=url)
        if respond.status_code !=200:
            return None
        data= respond.json()
        return data['data']['aqi']
        
    def fetch_geo_data(self,longitude:float,latitude:float):
        """ fetch geo data
            Args:
     def clean(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, tuple):
        return list(obj)
    return obj
           longitude (float): _description_
                latitude (float): _description_

            Returns:
                _type_: _description_
        """
        print('fetching geo data')

        city,indexes= self.get_city_from_point(longitude=longitude,latitude=latitude)
        tempature = self.get_tempature(longitude=longitude,latitude=latitude)
        aqi = self.get_aqi(longitude=longitude,latitude=latitude)
        data ={'city':city,'aqi':aqi,'tempature':tempature}
        return data 
    
    
    def get_geo_data(self,longitude:float,latitude:float):
        """get geo data from cache, if not exists then fetch

        Args:
            longitude (float): _description_
            latitude (float): _description_

        Returns:
            _type_: _description_
        """
        data = self.get_data_from_cache(longitude=longitude,latitude=latitude)
        if data is None:
            print('No data from cache')
            data = self.fetch_geo_data(longitude=longitude,latitude=latitude)
            self.add_data_to_cache(data=data,longitude=longitude,latitude=latitude)
        return data 
    
    def get_city(self,user_id,longitude:float,latitude:float):
        """get city from posible list on cache if not fetch

        Args:
            user_id (_type_): _description_
            longitude (float): _description_
            latitude (float): _description_

        Returns:
            _type_: _description_
        """
        indexes = self.get_possible_cities_indexes_from_cache(user_id=user_id)
        if indexes:
            print('get city from cache')

            city,indexes = self.get_city_from_point(longitude=longitude,latitude=latitude,posible_indx=indexes)
            if city:
                return city
        city,indexes = self.get_city_from_point(longitude=longitude,latitude=latitude)
        print('fetching city')

        if indexes:
            data = []
            for num in indexes:
                data.append(int(num))            
            self.add_possible_cities_indexes_to_cache(user_id=user_id,indexes=data)
        return city
    
   
    
    
    def add_data_to_cache(self,data:object,longitude:float,latitude:float):
        """add data to cache

        Args:
            data (object): _description_
            longitude (float): _description_
            latitude (float): _description_
        """
        print('data',data)
        longitude = round(longitude,2)
        latitude = round (latitude,2)
        key = f'{longitude}:{latitude}'
        self.cache.set(key=key,time=600,data=json.dumps(data))
        
    
    def add_possible_cities_indexes_to_cache(self,user_id,indexes:list):
        """add indexes of cities to cache

        Args:
            user_id (_type_): user_id
            indexes (list): indexes
        """
        key = f'user{user_id}_posible_indexes'
        data = json.dumps(indexes)
        self.cache.set(key=key,time=3600,data=data)
        
        
        
    def get_possible_cities_indexes_from_cache(self,user_id):
        """get indexes of posible cities in cache

        Args:
            user_id (_type_): user_id

        Returns:
            object: data or None
        """
        key = f'user{user_id}_posible_indexes'
        data = self.cache.get(key)
        if data:
            return json.loads(data)
        return None
    
    def get_data_from_cache(self,longitude:float,latitude:float):
        """return geo data from cache

        Args:
            longitude (float): longitude
            latitude (float): latitude

        Returns:
            object: data or None
        """
        longitude = round(longitude,2)
        latitude = round (latitude,2)
        key = f'{longitude}:{latitude}'
        data = self.cache.get(key)
        if data:
            return json.loads(data)
        return None