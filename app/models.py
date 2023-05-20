import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import app
from app import login

import psycopg2


class DataBase(object):
    _db_name = app.app.config['DB_NAME']
    _db_user = app.app.config['DB_USER']
    _user_password = app.app.config['USER_PASSWORD']
    _db_host = app.app.config['DB_HOST']
    _db_port = app.app.config['DB_PORT']

    _connection: psycopg2 = None

    @classmethod
    def _to_connect(cls):
        try:
            cls._connection = psycopg2.connect(
                database=cls._db_name,
                user=cls._db_user,
                password=cls._user_password,
                host=cls._db_host,
                port=cls._db_port,
            )
        except psycopg2.OperationalError as ex:
            print(f"{ex}")
        except Exception as ex:
            print(f'{ex}')
        else:
            print("connection is successful")
        return

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, is_returning: bool = False):
        if cls._connection is None:
            cls._to_connect()
        cls._connection.autocommit = True
        cursor = cls._connection.cursor()
        try:
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            if is_returning:
                result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'{ex}')
        except Exception as ex:
            print(f'{ex}')
        else:
            print("the query is executed")
            if is_returning:
                return result
            else:
                return True
        finally:
            cursor.close()
        return None


class User(UserMixin):
    def __init__(self,
                 id: int,
                 numb_phone,
                 e_mail,
                 login_dev: str,
                 password_hash: str):
        self.id = id
        self.numb_phone = numb_phone
        self.e_mail = e_mail
        self.login_dev = login_dev
        self.password_hash = password_hash

    def __repr__(self):
        return f'U id={self.id} login={self.login_dev}'

    def tuple(self):
        return (self.numb_phone,
                self.e_mail,
                self.login_dev,
                self.password_hash)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_id(cls, id: int):
        query = '''
        SELECT * 
        FROM profile
        WHERE id_profile = {}
        '''.format(id)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return User(* params)

    @classmethod
    def get_by_login(cls, login):
        query = '''
        SELECT * 
        FROM Profile
        WHERE login_dev = %s'''
        result = DataBase.execute_query(query, (login,), True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return User(* params)

    @classmethod
    def add(cls, user):
        query = '''
        INSERT INTO profile (numb_phone, e_mail, login_dev, password_dev_hash)
        VALUES {}
        '''.format(user.tuple())
        return DataBase.execute_query(query)

@login.user_loader
def load_user(id: str):
    user = User.get_by_id(int(id))
    print(f'user {user} loaded')
    return user

class Ad(object):
    def __init__(self,
                 ID_object,
                 name_object,
                 amount_rooms,
                 metr,
                 price,
                 floor,
                 type_of_deal,
                 description,
                 photo,
                 ID_profile,
                 ID_TypeObject,
                 ID_House):
        self.ID_object = ID_object
        self.name_object = name_object
        self.amount_rooms = amount_rooms
        self.metr = metr
        self.price = price
        self.floor = floor
        self.type_of_deal = type_of_deal
        self.description = description
        self.photo = photo
        self.ID_profile = ID_profile
        self.ID_TypeObject = ID_TypeObject
        self.ID_House = ID_House
        self.house = None

    def tuple(self):
        return(self.name_object,
               self.amount_rooms,
               self.metr,
               self.price,
               self.floor,
               self.type_of_deal,
               self.description,
               self.photo,
               self.ID_profile,
               self.ID_TypeObject,
               self.ID_House)

    @classmethod
    def add(cls, Ad):
        query = '''
        INSERT INTO Object (name_object, amount_rooms, metr, price, floor, 
        type_of_deal, description, photo, ID_profile, ID_TypeObject, ID_House)
        VALUES {}
        '''.format(Ad.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_all_with_params(cls,
                            with_params: bool = False,
                            name_object: str = None,
                            amount_rooms: int = None,
                            price: int = None,
                            type_of_deal: str = None):
        query = '''
        SELECT * FROM Object
        INNER JOIN House ON Object.ID_House = House.ID_House'''
        and_flag = False
        if with_params:
            query += '\nWHERE '
            if name_object is not None:
                query += " Object.name_object LIKE '%{}%' \n".format(name_object)
                and_flag = True
            if amount_rooms is not None:
                if and_flag:
                    query += ' and '
                query += ' Object.amount_rooms = {} \n'.format(amount_rooms)
                and_flag = True
            if price is not None:
                if and_flag:
                    query += ' and '
                query += ' Object.price <= {} \n'.format(price)
                and_flag = True
            if type_of_deal is not None:
                if and_flag:
                    query += ' and '
                query += ' Object.ID_TypeObject = {} \n'.format(type_of_deal)
                and_flag = True

        result = DataBase.execute_query(query, is_returning = True)
        if result is None:
            return None
        if len(result)==0:
            return []
        ads = []
        for item in result:
            ad = Ad(* item[:12:1])
            ad.house = House(* item[12:])
            ads.append(ad)
        return ads

    @classmethod
    def get_by_id(cls, adID):
        query = '''
        SELECT * FROM Object
        WHERE ID_object = {}'''.format(adID)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Ad(* params)


class TypeObject(object):
    def __init__(self,
                 ID_TypeObject,
                 name_of_type):
        self.ID_TypeObject = ID_TypeObject
        self.name_of_type = name_of_type

    @classmethod
    def get_all(cls):
        query = '''
                SELECT *
                FROM TypeObject'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result

class House(object):
    def __init__(self,
                 ID_House,
                 number,
                 building,
                 floorness,
                 ID_District,
                 ID_Street,
                 ID_Subway):
        self.ID_House = ID_House
        self.number = number
        self.building = building
        self.floorness = floorness
        self.ID_District = ID_District
        self.ID_Street = ID_Street
        self.ID_Subway = ID_Subway

    def tuple(self):
        return(self.number,
               self.building,
               self.floorness,
               self.ID_District,
               self.ID_Street,
               self.ID_Subway)

    @classmethod
    def add(cls, house):
        query = '''
        INSERT INTO House(number, building, floorness,
        ID_District, ID_Street, ID_Subway)
        VALUES {} 
        returning ID_House
        '''.format(house.tuple())
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result[0][0]

    @classmethod
    def get_by_id(cls, ID_House):
        query = '''
            SELECT * FROM House
            WHERE ID_House = {}'''.format(ID_House)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return House(*params)

class District(object):
    def __init__(self,
                 ID_District,
                 name_district,
                 ID_City):
        self.ID_District = ID_District
        self.name_district = name_district
        self.ID_City = ID_City

    @classmethod
    def get_all(cls):
        query = '''
               SELECT ID_District, name_district
               FROM District'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result

    def tuple(self):
        return(self.name_district,
               self.ID_City)

    @classmethod
    def add(cls, District):
        query = '''
        INSERT INTO District (name_district, ID_City)
        VALUES {}
        '''.format(District.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, ID_District):
        query = '''
                SELECT * FROM District
                WHERE ID_District = {}'''.format(ID_District)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return District(*params)

class Street(object):
    def __init__(self,
                 ID_Street,
                 name_street,
                 ID_City):
        self.ID_Street = ID_Street
        self.name_street = name_street
        self.ID_City = ID_City

    @classmethod
    def get_all(cls):
        query = '''
               SELECT ID_Street, name_street
               FROM Street'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result

    def tuple(self):
        return(self.name_street,
               self.ID_City)

    @classmethod
    def add(cls, Street):
        query = '''
        INSERT INTO Street (name_street, ID_City)
        VALUES {}
        '''.format(Street.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, ID_Street):
        query = '''
                    SELECT * FROM Street
                    WHERE ID_Street = {}'''.format(ID_Street)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Street(*params)

class Subway(object):
    def __init__(self,
                 ID_Subway,
                 name_subway,
                 ID_City):
        self.ID_Subway = ID_Subway
        self.name_subway = name_subway
        self.ID_City = ID_City

    @classmethod
    def get_all(cls):
        query = '''
               SELECT ID_Subway, name_subway
               FROM Subway'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result

    def tuple(self):
        return(self.name_subway,
               self.ID_City)

    @classmethod
    def add(cls, Subway):
        query = '''
        INSERT INTO Subway (name_subway, ID_City)
        VALUES {}
        '''.format(Subway.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, ID_Subway):
        query = '''
                    SELECT * FROM Subway
                    WHERE ID_Subway = {}'''.format(ID_Subway)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return Subway(*params)

class City(object):
    def __init__(self,
                 ID_City,
                 name_city):
        self.ID_City = ID_City
        self.name_city = name_city

    @classmethod
    def get_all(cls):
        query = '''
            SELECT *
            FROM City'''
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        return result

    def tuple(self):
        return(self.name_city)

    @classmethod
    def add(cls, City):
        query = '''
        INSERT INTO City (name_city)
        VALUES {}
        '''.format(City.tuple())
        return DataBase.execute_query(query)

    @classmethod
    def get_by_id(cls, ID_City):
        query = '''
                    SELECT * FROM City
                    WHERE ID_City = {}'''.format(ID_City)
        result = DataBase.execute_query(query, is_returning=True)
        if result is None or len(result) == 0:
            return None
        params = result[0]
        return City(*params)