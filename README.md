accounting/database.py is the database API
db/db_schema_dump.sql is the schema to dump 
db/db_data_dump.sql is the data to dump into the database

We have test our RESTful API using the plugin for Google Chrome DHC - REST/HTTP API Client (https://chrome.google.com/webstore/detail/dhc-resthttp-api-client/aejoelaoggembcahagimdiliamlcdmfm)

We have carried out the following tests:

use case:
request:

__USERS__

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/
request:POST

__USER__

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/<nickname>/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/<nickname>/
request:DELETE

__USERPUBLIC__

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/<nickname>/public_profile/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/<nickname>/public_profile/
request:PUT

__USERRESTRICTED__

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/<nickname>/restricted_profile/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/users/<nickname>/restricted_profile/
request:PUT

__INCOME__

use case: http://application/vnd.collection+json;127.0.0.1:5000//accounting/api/incomes/<id>/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000//accounting/api/incomes/<id>/
request:PUT

use case: http://application/vnd.collection+json;127.0.0.1:5000//accounting/api/incomes/<id>/
request:DELETE

__INCOMES__

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/incomes/<id>/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/incomes/<id>/
request:POST

__EXPENSE__

use case: http://application/vnd.collection+json;127.0.0.1:5000//accounting/api/expenses/<id>/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000//accounting/api/expenses/<id>/
request:PUT

use case: http://application/vnd.collection+json;127.0.0.1:5000//accounting/api/expenses/<id>/
request:DELETE

__EXPENSES__

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/user/<nickname>/expenses/
request:GET

use case: http://application/vnd.collection+json;127.0.0.1:5000/accounting/api/user/<nickname>/expenses/
request:POST



