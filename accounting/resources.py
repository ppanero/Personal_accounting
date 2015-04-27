import json

from flask import Flask, request, Response, g, jsonify
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

from utils import RegexConverter
import database

DEFAULT_DB_PATH = 'db/accounting.db'

#Constants for hypermedia formats and profiles
COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"
ACCOUNTING_USER_PROFILE = "http://schema.org/Person"
ACCOUNTING_INCOME_PROFILE = ""
ACCOUNTING_EXPENSE_PROFILE = ""

#Define the application and the api
app = Flask(__name__)
app.debug = True
#Set the database API. Change the DATABASE value from app.config to modify the
#database to be used (for instance for testing)
app.config.update({'DATABASE':database.AccountingDatabase(DEFAULT_DB_PATH)})
#Start the RESTful API.
api = Api(app)


def create_error_response(status_code, title, message, resource_type=None):
    response = jsonify(title=title, message=message, resource_type=resource_type)
    response.status_code = status_code
    return response

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found", "This resource url does not exit")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error", "The system has failed. Please, contact the administrator")

@app.before_request
def set_database():
    """
    Stores an instance of the database API before each request in the flas.g
    variable accessible only from the application context
    """
    g.db = app.config['DATABASE']



#Define the resources
class Users(Resource):

def get(self):
    """
    Gets a list of all the users in the database. It returns a status 
    code 200. 
    
                OUTPUT: 
         * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person

    Semantic descriptions used in items: nickname, registrationdate
    Link relations used in links: messages-all
    Semantic descriptors used in template: gender, nationality, age, nickname, firstName,
    lastName, email, birthday

    NOTE:
    In this case, we extract addressLocality and addressCountry from address
    and store in the database as addressLocality, addressCountry
    The property image links with the row picture in the database
    """
    #PERFORM OPERATIONS
    #Create the messages list
    users_db = g.db.get_users()

   #FILTER AND GENERATE THE RESPONSE
   #Create the envelope
    envelope = {}
    collection = {}
    envelope["collection"] = collection
    collection['version'] = "1.0"
    collection['href'] = api.url_for(Users)
    collection['template'] = {
      "data" : [
        {"prompt" : "Insert nickname", "name" : "nickname",
         "value" : "", "required":True},
        {"prompt" : "Insert user address", "name" : "gender",
         "object" : {}, "required":False},
        {"prompt" : "Insert user avatar", "name" : "nationality",
         "value" : "", "required":False},
        {"prompt" : "Insert user email", "name" : "firstName",
         "value" : "", "required":False},
        {"prompt" : "Insert user familyName", "name" : "lastName",
         "value" : "", "required":False},
        {"prompt" : "Insert user gender", "name" : "email",
         "value" : "", "required":False},
        {"prompt" : "Insert user givenName", "name" : "birthday",
         "value" : "", "required":False}]
    }
    #Create the items
    items = []
    for udb in users_db:
        _udb_nickname = udb['nickname']
        _url = api.url_for(User, nickname=_udb_nickname)
        udb = {}
        udb['href'] = _url
        udb['read-only'] = True
        udb['data'] = []
        value = {'name':'nickname', 'value':_nickname}
        udb['data'].append(value)
        items.append(udb)
    collection['items'] = items
    #RENDER
    return Response (json.dumps(envelope), 200, mimetype=COLLECTIONJSON+";"+ACCOUNTING_USER_PROFILE)

def post(self):
    """
    Adds a new user in the database.

    ENTITY BODY INPUT FORMAT:
    * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person

    The body should be a Collection+JSON template.         
    Semantic descriptors used in template: gender(mandatory),
    nationality(mandatory), nickname(mandatory), firstName(mandatory),
    lastName(mandatory), email(mandatory), birthday(mandatory).

    OUTPUT: 
    Returns 201 + the url of the new resource in the Location header
    Return 409 Conflict if there is another user with the same nickname
    Return 400 if the body is not well formed
    Return 415 if it receives a media type != application/json

    The rest of the properties match one-to-one with a column in the database

    NOTE:

    The database append_user receives a dictionary with the format:
    {'public_profile':{'nickname':''
                       'gender':'','nationality':'','birthday':''},
     'restricted_profile':{'firstname':'','lastname':'','email':''}
        }
    """
    #PARSE THE REQUEST:
    input = request.get_json(force=True)
    if not input:
        return create_error_response(415, "Unsupported Media Type",
                                     "Use a JSON compatible format",
                                     "User")
    #Get the request body and serialize it to object 
    #We should check that the format of the request body is correct. Check
    #That mandatory attributes are there.

    data = input['template']['data']

    _nickname = None
    _gender = None
    _nationality = None
    _firstname = None
    _lastname = None
    _birthday = None
    _email = None
   
    for d in data:
    #This code has a bad performance. We write it like this for
    #simplicity. Another alternative should be used instead. E.g. 
    #generation expressions
        if d['name'] == "nickname":
            _nickname = d['value']
        elif d['name'] == "gender":
            _gender = d['value']
        elif d['name'] == "nationality":
            _nationality = d['value']
        elif d['name'] == "firstname":
            _firstname = d['value']
        elif d['name'] == "birthday":
            _birthday = d['value']
        elif d['name'] == "email":
            _email = d['value']
        elif d['name'] == "lastname":
            _lastname = d['value']
    if not _birthday or not _email or not _lastname or \
    not _gender or not _firstname or not _nickname or not _nationality:
        return create_error_response(400, "Wrong request format",
                                          "Be sure you include all mandatory"\
                                          "properties",
                                          "User") 
    #Conflict if user already exist
    if g.db.contains_user(_nickname):
        return create_error_response(400, "Wrong nickname",
                                          "There is already a user with same nickname %s.\
                                           Try another one " % _nickname,
                                          "User")

    user =  {'public_profile':{'nickname': _nickname,
                               'gender':_gender,'nationality':_nationality, 'birthday':_birthday},
             'restricted_profile':{'firstname':_firstname,
                                  'lastname':_lastname,
                                  'email':_email}
    }
    

    #But we are not going to do this exercise
    nickname = g.db.append_user(_nickname, user)

    #CREATE RESPONSE AND RENDER
    return  Response(status=201, 
                     headers={"Location":api.url_for(User, 
                                                     nickname=nickname)}
                    )
    
class User(Resource):
    """
    User Resource. Public and private profile are separate resources.
    """
    def _isauthorized(self, nickname, authorization): 
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to 
        authorize.
        """
        if authorization is not None and \
                                (authorization.lower() == "admin" or 
                                 authorization.lower() == nickname.lower()):
            return True
        return False

    def get(self, nickname): 
        """
        Get basic information of a user:

        INPUT PARAMETER:
        - nickname: A string containing the nickname of the required user. 

        OUTPUT:
        Return 200 if the nickname exists.
        Return 404 if the nickname is not stored in the system.
         
       
        ENTITY BODY OUTPUT FORMAT: 
         * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person
        Link relations used: self, collection, public-data, private-data
        Semantic descriptors used: nickname

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'public_profile':{'nickname':''
	                       'gender':'','nationality':'','birthday':''},
	     'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }

        """
        #PERFORM OPERATIONS
        user_db = g.db.get_user(nickname)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with nickname %s" 
                                         % nickname,
                                         "User")
        
        #FILTER AND GENERATE RESPONSE
                #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(User, nickname=nickname),
                         'profile': ACCOUNTING_USER_PROFILE}
        links['collection'] = {'href':api.url_for(Users),
                               'profile': ACCOUNTING_USER_PROFILE,
                               'type':COLLECTIONJSON}
        links['public-data'] = {
                            'href':api.url_for(User_public, nickname=nickname),
                            'profile': ACCOUNTING_USER_PROFILE,
                            'type':COLLECTIONJSON}
        links['restricted-data'] = {
                            'href':api.url_for(User_restricted, nickname=nickname),
                            'profile': ACCOUNTING_USER_PROFILE,
                            'type':COLLECTIONJSON}       

        envelope['nickname'] = nickname


        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_USER_PROFILE)

    def delete(self, nickname):
        """
        Delete a user in the system if the user is authorized to do so.
        A user is authorized if the 'Authorization' header contains either
        admin or the nickname of the user to be deleted.

        OUTPUT:

        If the user is authorized delete the given user and returns 204.
        If the user is not authorized return 401
        If the nickname does not exist return 404
        """
        #PERFORM AUTHORIZATION CHECKING
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass

        #PEROFRM OPERATIONS
        #Try to delete the user. If it could not be deleted, the database
        #returns None.
        if self._isauthorized(nickname, authorization):
            if g.db.delete_user(nickname):
                #RENDER RESPONSE
                return '', 204
            else:
                #GENERATE ERROR RESPONSE
                return create_error_response(404, "Unknown user",
                                        "There is no a user with nickname %s" 
                                         % nickname,
                                         "User")
        else:
            #User is not authorized
            return create_error_response(401, "Unauthorized",
                                         "Please, provide credentials",
                                         "User")

class UserPublic(Resource):
    def _isauthorized(self, nickname, authorization): 
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to 
        authorize.
        """
        if authorization is not None and \
                                (authorization.lower() == "admin" or 
                                 authorization.lower() == nickname.lower()):
            return True
        return False

    def get (self, nickname):
        """
        Gets the public representation of a user. 

        INPUT PARAMETER:
        - nickname: A string containing the nickname of the required user. 

        OUTPUT:
        Return 200 if the nickname exists.
        Return 404 if the nickname is not stored in the system.
         
        ENTITY BODY OUTPUT FORMAT: 
         * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person
        Link relations used: self, parent, private-data, edit.
        Semantic descriptors used: nickname

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'public_profile':{'nickname':''
	                       'gender':'','nationality':'','birthday':''},
	        }

        """
        #PERFORM OPERATIONS
        user_db = g.db.get_user(nickname)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with nickname %s" 
                                         % nickname,
                                         "User")
        
        #FILTER AND GENERATE RESPONSE
                #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(UserPublic, nickname=nickname),
                         'profile': ACCOUNTING_USER_PROFILE}
        links['parent'] = {'href':api.url_for(User, nickname=nickname),
                           'profile': ACCOUNTING_USER_PROFILE,
                           'type':HAL}
        links['private-data'] = {
                            'href':api.url_for(User_restricted, 
                                               nickname=nickname),
                            'profile': ACCOUNTING_USER_PROFILE,
                            'type':HAL}
        links['edit'] = {
                            'href':api.url_for(UserPublic, nickname=nickname),
                            'profile': ACCOUNTING_USER_PROFILE,
                            'type':COLLECTIONJSON} 
            

        envelope['nickname'] = nickname        
        envelope['gender'] = user_db['public_profile']['gender']
        envelope['nationality'] = user_db['public_profile']['nationality']
        envelope['birthday'] = user_db['public_profile']['birthday']
        envelope['template'] = { "data" : [ 
                                            {"prompt" : "Insert gender text",
                                             "name" : "gender",
                                             "value" : "",
                                             "required":True}, 
                                            {"prompt" : "Insert nationality file name",
                                             "name" : "nationality",
                                             "value" : "",
                                             "required":True},
                                             {"prompt" : "Insert birthday file name",
                                             "name" : "birthday",
                                             "value" : "",
                                             "required":True}
                                        ]                             
                                }


        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_USER_PROFILE)

    def put (self, nickname):
        """
        Modifies the avatar and signature of a user. Only authorized users can
        make the modifictation

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person

        The body should be a Collection+JSON template.         
        Semantic descriptors used in template: signature, avatar. 
         INPUT PARAMETER:
        - nickname: A string containing the nickname of the user to modify 

        OUTPUT:
        Returns 204 if the message is modified correctly
        Returns 400 if the body of the request is not well formed or it is
        empty.
        Returns 401 if the user is not authorized
        Returns 404 if there is no message with messageid
        Returns 415 if the input is not JSON.

        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                     "You should be authorized to edit this data",
                                     "User_public")

        #CHECK THAT MESSAGE EXISTS
        if not g.db.contains_user(nickname):
            raise NotFound()

        #PARSE THE REQUEST
        #Extract the request body. In general would be request.data
        #Since the request is JSON I use request.get_json
        #get_json returns a python dictionary after serializing the request body
        #get_json returns None if the body of the request is not formatted
        # using JSON
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                     "Use a JSON compatible format",
                                     "User_public")


        #It throws a BadRequest exception, and hence a 400 code if the JSON is 
        #not wellformed
        try: 
            data = input['template']['data']
            _gender = None
            _birthday = None
            _nationality = None
            for d in data: 
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead.
                if d['name'] == "birthday":
	                _birthday ["birthday"] = d['value']
                elif d['name'] == "nationality":
	                _nationality ["nationality"] = d['value']
                elif d['name'] == "gender":
	                _gender ["gender"] = d['value']
            #CHECK THAT DATA RECEIVED IS CORRECT
            if not _gender or not _birthday or not _nationality:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include gender, nationality and birthday",
                                             "User_public")
        except: 
            #This is launched if either gender or nationality or birthday does not exist or the 
            #template.data is not there. 
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include gender, nationality and birthday",
                                          "User_public")
        else:
            user = {'public_profile':{'gender':_gender,'nationality':_nationality,'birthday':_birthday}}
            if not g.db.modify_user(nickname, user):
                return NotFound()
            return '', 204

class UserRestricted(Resource):
    def _isauthorized(self, nickname, authorization): 
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to 
        authorize.
        """
        if authorization is not None and \
                                (authorization.lower() == "admin" or 
                                 authorization.lower() == nickname.lower()):
            return True
        return False
    
    def get (self, nickname):
        """
        Gets the restricted representation of a user. Only authorzed users 
        are allowed to modify it. 

        INPUT PARAMETER:
        - nickname: A string containing the nickname of the required user. 

        OUTPUT:
        Return 200 if the nickname exists.
        Return 404 if the nickname is not stored in the system.
        Return 401 if the user is not authorized
         
        ENTITY BODY OUTPUT FORMAT: 
         * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person
        Link relations used: self, parent, public-data, edit.
        Semantic descriptors used: firstname, lastname, email.

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }
        }
        



        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                     "You should be authorized to edit this data",
                                     "User_restricted")
        #PERFORM OPERATIONS
        user_db = g.db.get_user(nickname)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with nickname %s" 
                                         % nickname,
                                         "User_restricted")
        
        #FILTER AND GENERATE RESPONSE
                #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(UserPublic, nickname=nickname),
                         'profile': ACCOUNTING_USER_PROFILE}
        links['parent'] = {'href':api.url_for(User, nickname=nickname),
                           'profile': ACCOUNTING_USER_PROFILE,
                           'type':HAL}
        links['public-data'] = {
                            'href':api.url_for(UserPublic,
                                               nickname=nickname),
                            'profile': ACCOUNTING_USER_PROFILE,
                            'type':HAL}
        links['edit'] = {
                            'href':api.url_for(UserRestricted, nickname=nickname),
                            'profile': ACCOUNTING_USER_PROFILE,
                            'type':COLLECTIONJSON}

        envelope['nickname'] = nickname
        
        
        envelope['email'] = user_db['restricted_profile']['email']
        envelope['firstname'] = user_db['restricted_profile']['firstname']
        envelope['lastname'] = user_db['restricted_profile']['lastname']
        envelope['template'] = { "data" : [ 
                                           {"prompt" : "Insert user email",
                                             "name" : "email",
                                             "value" : "",
                                             "required":True},
                                            {"prompt" : "Insert user firstname",
                                             "name" : "firstname",
                                             "value" : "",
                                             "required":True},
                                            {"prompt" : "Insert user lastname",
                                             "name" : "lastname",
                                             "value" : "",
                                             "required":True},
                                        ] 
                                }
        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_USER_PROFILE)

    def put (self, nickname):
        """
        Modifies an existing user. Only authorized users are allowed.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON: 
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile: 
            http://schema.org/Person

        The body should be a Collection+JSON template.         
        Semantic descriptors used in template: email(mandatory),
        firstname(mandatory), lastname(mandatory).

        OUTPUT: 
        Return 204 if the restricted profile could be modified
        Return 401 if the user is not authorized
        Return 400 if the body is not well formed
        Return 415 if it receives a media type != application/json


        NOTE:

        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }


        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                     "You should be authorized to edit this data",
                                     "User_restricted")
        #Check user exists:
        user_db = g.db.get_user(nickname)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with nickname %s" 
                                         % nickname,
                                         "User_restricted")
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "User_restricted")
        #Get the request body and serialize it to object 
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.
        try:
            data = input['template']['data']
        except:
            return create_error_response(400, "Bad format",
                                         "You must embed the data in a Collection+JSON template",
                                 "User_restricted")

        _temp_dictionary = {}
        for d in data:
        #This code has a bad performance. We write it like this for
        #simplicity. Another alternative should be used instead. E.g. 
        #generation expressions
            if d['name'] == "email":
                _temp_dictionary ["email"] = d['value']
            elif d['name'] == "lastName":
                _temp_dictionary ["lastname"] = d['value']
            elif d['name'] == "firstName":
                _temp_dictionary ["firstname"] = d['value']


        for key in ("email", "lastname", "firstname"):
            if key not in _temp_dictionary:
                return create_error_response(400, "Wrong request format",
                                              "Be sure you include all mandatory"\
                                              "properties: "+ key + " missing",
                                              "User_restricted")
             
        user =  {'restricted_profile':{'firstname':_temp_dictionary['firstname'],
                                       'lastname':_temp_dictionary['lastname'],
                                       'email':_temp_dictionary['email'],
                                       }
                }
        g.db.modify_user(nickname, user)

        #CREATE RESPONSE AND RENDER
        return  Response(status=204)

class Income(Resource):
    def _isauthorized(self, nickname, authorization):
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to
        authorize.
        """
        if authorization is not None and \
                (authorization.lower() == "admin" or
                         authorization.lower() == nickname.lower()):
            return True
        return False

    def get (self, id, nickname):
        """
        Gets an specific (by id) income. Only authorzed users
        are allowed to modify it.

        INPUT PARAMETER:
        - id: A string containing the id of the required income.

        OUTPUT:
        Return 200 if the id exists.
        Return 404 if the id is not stored in the system.
        Return 401 if the user is not authorized

        ENTITY BODY OUTPUT FORMAT:
         * Media type: Collection+JSON:
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile:
            http://schema.org/Person
        Link relations used: self, parent, public-data, edit.
        Semantic descriptors used: firstname, lastname, email.

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }
        }
        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                         "You should be authorized to edit this data",
                                         "User_restricted")
        #PERFORM OPERATIONS
        income_db = g.db.get_income(id)
        if not income_db:
            return create_error_response(404, "Unknown income",
                                         "There is no a income with id %s"
                                         % id,
                                         "Income")

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(Income, id=id),
                         'profile': ACCOUNTING_INCOME_PROFILE}
        links['parent'] = {'href':api.url_for(User, nickname=nickname),
                           'profile': ACCOUNTING_USER_PROFILE,
                           'type':HAL}

        envelope['_id'] = id
        envelope['user_id'] = income_db['user_id']
        envelope['source'] = income_db['source']
        envelope['amount'] = income_db['amount']
        envelope['description'] = income_db['description']
        envelope['date'] = income_db['date']
        envelope['template'] = { "data" : [
            {"prompt" : "", "name" : "source", "value" : "", "required":True},
            {"prompt" : "", "name" : "amount", "value" : "", "required":True},
            {"prompt" : "", "name" : "date", "value" : "", "required": True},
            {"prompt" : "", "name" : "description", "value" : "", "required": False},
            {"prompt" : "", "name" : "bill_image", "value" : "", "required": False},
            {"prompt" : "", "name" : "user_id", "value" : "", "required": True},
            ]
        }
        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_INCOME_PROFILE)

    def put (self, id, nickname):
        """
        Modifies an existing user. Only authorized users are allowed.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON:
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile:
            http://schema.org/Person

        The body should be a Collection+JSON template.
        Semantic descriptors used in template: email(mandatory),
        firstname(mandatory), lastname(mandatory).

        OUTPUT:
        Return 204 if the restricted profile could be modified
        Return 401 if the user is not authorized
        Return 400 if the body is not well formed
        Return 415 if it receives a media type != application/json


        NOTE:

        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }


        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                         "You should be authorized to edit this data",
                                         "User_restricted")
        #Check user exists:
        income_db = g.db.get_income(id)
        if not income_db:
            return create_error_response(404, "Unknown income",
                                         "There is no a income with id %s"
                                         % id,
                                         "Income")
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "Income")
        #Get the request body and serialize it to object
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.
        try:
            data = input['template']['data']
        except:
            return create_error_response(400, "Bad format",
                                         "You must embed the data in a Collection+JSON template",
                                         "Income")

        _temp_dictionary = {}
        for d in data:
            #This code has a bad performance. We write it like this for
            #simplicity. Another alternative should be used instead. E.g.
            #generation expressions
            if d['name'] == "source":
                _temp_dictionary ["source"] = d['value']
            elif d['name'] == "amount":
                _temp_dictionary ["amount"] = d['value']
            elif d['name'] == "date":
                _temp_dictionary ["date"] = d['value']
            elif d['name'] == "description":
                _temp_dictionary ["description"] = d['value']


        for key in ("source", "amount", "date", "description"):
            if key not in _temp_dictionary:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include all mandatory" \
                                             "properties: "+ key + " missing",
                                             "Income")

        g.db.modify_income(id, _temp_dictionary ["source"], _temp_dictionary ["amount"],
                           _temp_dictionary ["date"], _temp_dictionary ["description"])

        #CREATE RESPONSE AND RENDER
        return  Response(status=204)

    def delete(self, id, nickname):
        """
        Delete a user in the system if the user is authorized to do so.
        A user is authorized if the 'Authorization' header contains either
        admin or the nickname of the user to be deleted.

        OUTPUT:

        If the user is authorized delete the given user and returns 204.
        If the user is not authorized return 401
        If the nickname does not exist return 404
        """
        #PERFORM AUTHORIZATION CHECKING
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass

        #PEROFRM OPERATIONS
        #Try to delete the user. If it could not be deleted, the database
        #returns None.
        if self._isauthorized(nickname, authorization):
            if g.db.delete_income(id):
                #RENDER RESPONSE
                return '', 204
            else:
                #GENERATE ERROR RESPONSE
                return create_error_response(404, "Unknown income",
                                             "There is no a income with id %s"
                                             % id,
                                             "Income")
        else:
            #User is not authorized
            return create_error_response(401, "Unauthorized",
                                         "Please, provide credentials",
                                         "User")

class Expense(Resource):
    def _isauthorized(self, nickname, authorization):
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to
        authorize.
        """
        if authorization is not None and \
                (authorization.lower() == "admin" or
                         authorization.lower() == nickname.lower()):
            return True
        return False

    def get (self, id, nickname):
        """
        Gets an specific (by id) expense. Only authorzed users
        are allowed to modify it.

        INPUT PARAMETER:
        - id: A string containing the id of the required expense.

        OUTPUT:
        Return 200 if the id exists.
        Return 404 if the id is not stored in the system.
        Return 401 if the user is not authorized

        ENTITY BODY OUTPUT FORMAT:
         * Media type: Collection+JSON:
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile:
            http://schema.org/Person
        Link relations used: self, parent, public-data, edit.
        Semantic descriptors used: firstname, lastname, email.

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }
        }
        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                         "You should be authorized to edit this data",
                                         "User_restricted")
        #PERFORM OPERATIONS
        expense_db = g.db.get_expense(id)
        if not expense_db:
            return create_error_response(404, "Unknown expense",
                                         "There is no a expense with id %s"
                                         % id,
                                         "expense")

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(Expense, id=id),
                         'profile': ACCOUNTING_EXPENSE_PROFILE}
        links['parent'] = {'href':api.url_for(User, nickname=nickname),
                           'profile': ACCOUNTING_USER_PROFILE,
                           'type':HAL}

        envelope['_id'] = id
        envelope['user_id'] = expense_db['user_id']
        envelope['source'] = expense_db['source']
        envelope['amount'] = expense_db['amount']
        envelope['description'] = expense_db['description']
        envelope['date'] = expense_db['date']
        envelope['template'] = { "data" : [
            {"prompt" : "", "name" : "source", "value" : "", "required":True},
            {"prompt" : "", "name" : "amount", "value" : "", "required":True},
            {"prompt" : "", "name" : "date", "value" : "", "required": True},
            {"prompt" : "", "name" : "description", "value" : "", "required": False},
            {"prompt" : "", "name" : "bill_image", "value" : "", "required": False},
            {"prompt" : "", "name" : "user_id", "value" : "", "required": True},
            ]
        }
        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_EXPENSE_PROFILE)

    def put (self, id, nickname):
        """
        Modifies an existing user. Only authorized users are allowed.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON:
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile:
            http://schema.org/Person

        The body should be a Collection+JSON template.
        Semantic descriptors used in template: email(mandatory),
        firstname(mandatory), lastname(mandatory).

        OUTPUT:
        Return 204 if the restricted profile could be modified
        Return 401 if the user is not authorized
        Return 400 if the body is not well formed
        Return 415 if it receives a media type != application/json


        NOTE:

        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }


        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                         "You should be authorized to edit this data",
                                         "User_restricted")
        #Check user exists:
        expense_db = g.db.get_expense(id)
        if not expense_db:
            return create_error_response(404, "Unknown expense",
                                         "There is no a expense with id %s"
                                         % id,
                                         "expense")
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "expense")
        #Get the request body and serialize it to object
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.
        try:
            data = input['template']['data']
        except:
            return create_error_response(400, "Bad format",
                                         "You must embed the data in a Collection+JSON template",
                                         "expense")

        _temp_dictionary = {}
        for d in data:
            #This code has a bad performance. We write it like this for
            #simplicity. Another alternative should be used instead. E.g.
            #generation expressions
            if d['name'] == "source":
                _temp_dictionary ["source"] = d['value']
            elif d['name'] == "amount":
                _temp_dictionary ["amount"] = d['value']
            elif d['name'] == "date":
                _temp_dictionary ["date"] = d['value']
            elif d['name'] == "description":
                _temp_dictionary ["description"] = d['value']


        for key in ("source", "amount", "date", "description"):
            if key not in _temp_dictionary:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include all mandatory" \
                                             "properties: "+ key + " missing",
                                             "expense")

        g.db.modify_expense(id, _temp_dictionary ["source"], _temp_dictionary ["amount"],
                           _temp_dictionary ["date"], _temp_dictionary ["description"])

        #CREATE RESPONSE AND RENDER
        return  Response(status=204)

    def delete(self, id, nickname):
        """
        Delete a user in the system if the user is authorized to do so.
        A user is authorized if the 'Authorization' header contains either
        admin or the nickname of the user to be deleted.

        OUTPUT:

        If the user is authorized delete the given user and returns 204.
        If the user is not authorized return 401
        If the nickname does not exist return 404
        """
        #PERFORM AUTHORIZATION CHECKING
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass

        #PEROFRM OPERATIONS
        #Try to delete the user. If it could not be deleted, the database
        #returns None.
        if self._isauthorized(nickname, authorization):
            if g.db.delete_expense(id):
                #RENDER RESPONSE
                return '', 204
            else:
                #GENERATE ERROR RESPONSE
                return create_error_response(404, "Unknown expense",
                                             "There is no a expense with id %s"
                                             % id,
                                             "expense")
        else:
            #User is not authorized
            return create_error_response(401, "Unauthorized",
                                         "Please, provide credentials",
                                         "User")

class Incomes(Resource):
    def _isauthorized(self, nickname, authorization):
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to
        authorize.
        """
        if authorization is not None and \
                (authorization.lower() == "admin" or
                         authorization.lower() == nickname.lower()):
            return True
        return False

    def get (self, id, nickname):
        """
        Gets an specific (by id) expense. Only authorzed users
        are allowed to modify it.

        INPUT PARAMETER:
        - id: A string containing the id of the required expense.

        OUTPUT:
        Return 200 if the id exists.
        Return 404 if the id is not stored in the system.
        Return 401 if the user is not authorized

        ENTITY BODY OUTPUT FORMAT:
         * Media type: Collection+JSON:
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile:
            http://schema.org/Person
        Link relations used: self, parent, public-data, edit.
        Semantic descriptors used: firstname, lastname, email.

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }
        }
        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                         "You should be authorized to edit this data",
                                         "User_restricted")
        #PERFORM OPERATIONS
        expense_db = g.db.get_expense(id)
        if not expense_db:
            return create_error_response(404, "Unknown expense",
                                         "There is no a expense with id %s"
                                         % id,
                                         "expense")

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(Expense, id=id),
                         'profile': ACCOUNTING_EXPENSE_PROFILE}
        links['parent'] = {'href':api.url_for(User, nickname=nickname),
                           'profile': ACCOUNTING_USER_PROFILE,
                           'type':HAL}

        envelope['_id'] = id
        envelope['user_id'] = expense_db['user_id']
        envelope['source'] = expense_db['source']
        envelope['amount'] = expense_db['amount']
        envelope['description'] = expense_db['description']
        envelope['date'] = expense_db['date']
        envelope['template'] = { "data" : [
            {"prompt" : "", "name" : "source", "value" : "", "required":True},
            {"prompt" : "", "name" : "amount", "value" : "", "required":True},
            {"prompt" : "", "name" : "date", "value" : "", "required": True},
            {"prompt" : "", "name" : "description", "value" : "", "required": False},
            {"prompt" : "", "name" : "bill_image", "value" : "", "required": False},
            {"prompt" : "", "name" : "user_id", "value" : "", "required": True},
            ]
        }
        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_EXPENSE_PROFILE)
    def post(self):
        """
        Adds a new user in the database.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON:
             http://amundsen.com/media-types/collection/
             - Extensions: template validation and value-types
               https://github.com/collection-json/extensions
            * Profile:
                http://schema.org/Person

        The body should be a Collection+JSON template.
        Semantic descriptors used in template: gender(mandatory),
        nationality(mandatory), nickname(mandatory), firstName(mandatory),
        lastName(mandatory), email(mandatory), birthday(mandatory).

        OUTPUT:
        Returns 201 + the url of the new resource in the Location header
        Return 409 Conflict if there is another user with the same nickname
        Return 400 if the body is not well formed
        Return 415 if it receives a media type != application/json

        The rest of the properties match one-to-one with a column in the database

        NOTE:

        The database append_user receives a dictionary with the format:
        {'public_profile':{'nickname':''
                           'gender':'','nationality':'','birthday':''},
         'restricted_profile':{'firstname':'','lastname':'','email':''}
            }
        """
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "User")
        #Get the request body and serialize it to object
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.

        data = input['template']['data']

        _nickname = None
        _gender = None
        _nationality = None
        _firstname = None
        _lastname = None
        _birthday = None
        _email = None

        for d in data:
            #This code has a bad performance. We write it like this for
            #simplicity. Another alternative should be used instead. E.g.
            #generation expressions
            if d['name'] == "nickname":
                _nickname = d['value']
            elif d['name'] == "gender":
                _gender = d['value']
            elif d['name'] == "nationality":
                _nationality = d['value']
            elif d['name'] == "firstname":
                _firstname = d['value']
            elif d['name'] == "birthday":
                _birthday = d['value']
            elif d['name'] == "email":
                _email = d['value']
            elif d['name'] == "lastname":
                _lastname = d['value']
        if not _birthday or not _email or not _lastname or \
                not _gender or not _firstname or not _nickname or not _nationality:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory" \
                                         "properties",
                                         "User")
            #Conflict if user already exist
        if g.db.contains_user(_nickname):
            return create_error_response(400, "Wrong nickname",
                                         "There is already a user with same nickname %s.\
                                          Try another one " % _nickname,
                                         "User")

        user =  {'public_profile':{'nickname': _nickname,
                                   'gender':_gender,'nationality':_nationality, 'birthday':_birthday},
                 'restricted_profile':{'firstname':_firstname,
                                       'lastname':_lastname,
                                       'email':_email}
        }


        #But we are not going to do this exercise
        nickname = g.db.append_user(_nickname, user)

        #CREATE RESPONSE AND RENDER
        return  Response(status=201,
                         headers={"Location":api.url_for(User,
                                                         nickname=nickname)}
        )

class Expenses(Resource):
    def _isauthorized(self, nickname, authorization):
        """
        Check if a user is authorized or not to perform certain operation.

        This is a simple implementation of this method. Just checks that the
        authorization token is either admin or the nickname of the user to
        authorize.
        """
        if authorization is not None and \
                (authorization.lower() == "admin" or
                         authorization.lower() == nickname.lower()):
            return True
        return False

    def get (self, id, nickname):
        """
        Gets an specific (by id) expense. Only authorzed users
        are allowed to modify it.

        INPUT PARAMETER:
        - id: A string containing the id of the required expense.

        OUTPUT:
        Return 200 if the id exists.
        Return 404 if the id is not stored in the system.
        Return 401 if the user is not authorized

        ENTITY BODY OUTPUT FORMAT:
         * Media type: Collection+JSON:
         http://amundsen.com/media-types/collection/
         - Extensions: template validation and value-types
           https://github.com/collection-json/extensions
        * Profile:
            http://schema.org/Person
        Link relations used: self, parent, public-data, edit.
        Semantic descriptors used: firstname, lastname, email.

        NOTE: Format of the database
        The database append_user receives a dictionary with the format:
	    {'restricted_profile':{'firstname':'','lastname':'','email':''}
	        }
        }
        """
        #CHECK IF THE USER IS AUTHORIZED TO EDIT THIS DATA
        authorization = None
        try:
            authorization = request.headers["authorization"]
        except KeyError:
            pass
        if not self._isauthorized(nickname, authorization):
            return create_error_response(401, "Unauthorized",
                                         "You should be authorized to edit this data",
                                         "User_restricted")
        #PERFORM OPERATIONS
        expense_db = g.db.get_expense(id)
        if not expense_db:
            return create_error_response(404, "Unknown expense",
                                         "There is no a expense with id %s"
                                         % id,
                                         "expense")

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        links['self'] = {'href':api.url_for(Expense, id=id),
                         'profile': ACCOUNTING_EXPENSE_PROFILE}
        links['parent'] = {'href':api.url_for(User, nickname=nickname),
                           'profile': ACCOUNTING_USER_PROFILE,
                           'type':HAL}

        envelope['_id'] = id
        envelope['user_id'] = expense_db['user_id']
        envelope['source'] = expense_db['source']
        envelope['amount'] = expense_db['amount']
        envelope['description'] = expense_db['description']
        envelope['date'] = expense_db['date']
        envelope['template'] = { "data" : [
            {"prompt" : "", "name" : "source", "value" : "", "required":True},
            {"prompt" : "", "name" : "amount", "value" : "", "required":True},
            {"prompt" : "", "name" : "date", "value" : "", "required": True},
            {"prompt" : "", "name" : "description", "value" : "", "required": False},
            {"prompt" : "", "name" : "bill_image", "value" : "", "required": False},
            {"prompt" : "", "name" : "user_id", "value" : "", "required": True},
            ]
        }
        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+ACCOUNTING_EXPENSE_PROFILE)
    def post(self):
        """
        Adds a new user in the database.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON:
             http://amundsen.com/media-types/collection/
             - Extensions: template validation and value-types
               https://github.com/collection-json/extensions
            * Profile:
                http://schema.org/Person

        The body should be a Collection+JSON template.
        Semantic descriptors used in template: gender(mandatory),
        nationality(mandatory), nickname(mandatory), firstName(mandatory),
        lastName(mandatory), email(mandatory), birthday(mandatory).

        OUTPUT:
        Returns 201 + the url of the new resource in the Location header
        Return 409 Conflict if there is another user with the same nickname
        Return 400 if the body is not well formed
        Return 415 if it receives a media type != application/json

        The rest of the properties match one-to-one with a column in the database

        NOTE:

        The database append_user receives a dictionary with the format:
        {'public_profile':{'nickname':''
                           'gender':'','nationality':'','birthday':''},
         'restricted_profile':{'firstname':'','lastname':'','email':''}
            }
        """
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "User")
        #Get the request body and serialize it to object
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.

        data = input['template']['data']

        _nickname = None
        _gender = None
        _nationality = None
        _firstname = None
        _lastname = None
        _birthday = None
        _email = None

        for d in data:
            #This code has a bad performance. We write it like this for
            #simplicity. Another alternative should be used instead. E.g.
            #generation expressions
            if d['name'] == "nickname":
                _nickname = d['value']
            elif d['name'] == "gender":
                _gender = d['value']
            elif d['name'] == "nationality":
                _nationality = d['value']
            elif d['name'] == "firstname":
                _firstname = d['value']
            elif d['name'] == "birthday":
                _birthday = d['value']
            elif d['name'] == "email":
                _email = d['value']
            elif d['name'] == "lastname":
                _lastname = d['value']
        if not _birthday or not _email or not _lastname or \
                not _gender or not _firstname or not _nickname or not _nationality:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all mandatory" \
                                         "properties",
                                         "User")
            #Conflict if user already exist
        if g.db.contains_user(_nickname):
            return create_error_response(400, "Wrong nickname",
                                         "There is already a user with same nickname %s.\
                                          Try another one " % _nickname,
                                         "User")

        user =  {'public_profile':{'nickname': _nickname,
                                   'gender':_gender,'nationality':_nationality, 'birthday':_birthday},
                 'restricted_profile':{'firstname':_firstname,
                                       'lastname':_lastname,
                                       'email':_email}
        }


        #But we are not going to do this exercise
        nickname = g.db.append_user(_nickname, user)

        #CREATE RESPONSE AND RENDER
        return  Response(status=201,
                         headers={"Location":api.url_for(User,
                                                         nickname=nickname)}
        )

#Add the Regex Converter so we can use regex expressions when we define the
#routes
app.url_map.converters['regex'] = RegexConverter


#Define the routes
api.add_resource(Users, '/accounting/api/users/',
                 endpoint='users')
api.add_resource(User, '/accounting/api/users/<nickname>/',
                 endpoint='user')
api.add_resource(UserPublic, '/accounting/api/users/<nickname>/public_profile/',
                 endpoint='public_profile')
api.add_resource(UserRestricted, '/accounting/api/users/<nickname>/restricted_profile/',
                 endpoint='restricted_profile')
api.add_resource(Incomes, '/accounting/api/user/<nickname>/incomes/',
                 endpoint='user')
api.add_resource(Expenses, '/accounting/api/user/<nickname>/expenses/',
                 endpoint='user')
api.add_resource(Income, '/accounting/api/incomes/<id>/',
                 endpoint='incomes')
api.add_resource(Expense, '/accounting/api/expenses/<id>/',
                 endpoint='expenses')


#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug True activates automatic code reloading and improved error messages
    app.run(debug=True)