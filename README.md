To deploy and populate the database follow these steps (Although one is provided with the project):

1- Go to the project folder
2- Open a python console/terminal
    [In the python console]
        >> db_path = 'db/accounting.db'
        >> import accounting.database
        >> db = accounting.database.AccountingDatabase(db_path)
4- Then open a sqlite3 console/terminal
    [In the sqlite3 console]
        >> .open db/accounting.db
        >> .read db/db_schema_dump.sql
        >> .read db/db_data_dump.sql
    [You can check that the database is properly created by executing e.g. ".tables" or "select * from user"]


To test the application we should run the app with:
python -m personalaccounting
Path: http://127.0.0.1:5000/

We have tested our RESTful API using the plugin for Google Chrome DHC - REST/HTTP API Client (https://chrome.google.com/webstore/detail/dhc-resthttp-api-client/aejoelaoggembcahagimdiliamlcdmfm)
We have carried out the following tests:


users
-----

GET: 127.0.0.1:5000/accounting/api/users/ --> 200

    curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/users/'

DELETE: 127.0.0.1:5000/accounting/api/users/ --> 405

    curl -i -X DELETE \ 'http://127.0.0.1:5000/accounting/api/users/'

POST: 127.0.0.1:5000/accounting/api/users/ --> 201

    body:
    { "template" : {
        "data" : [
            {"prompt" : "Insert user birthday", "name" : "birthday", "value" : "19-04-1991"},
            {"prompt" : "Insert user email", "name" : "email", "value" : "hola@email.com"},
            {"prompt" : "Insert user firstName", "name" : "firstname", "value" : "Mick"},
            {"prompt" : "Insert user gender", "name" : "gender", "value" : "male"},
            {"prompt" : "Insert user gender", "name" : "nickname", "value" : "gio"},
            {"prompt" : "Insert user gender", "name" : "password", "value" : "testtest"},
            {"prompt" : "Insert user gender", "name" : "balance", "value" : "0"}
        ]
        }
    } 

POST: 127.0.0.1:5000/accounting/api/users/ --> 400

    body:
    { "template" : {
        "data" : [
            {"prompt" : "Insert user birthday", "name" : "birthday", "value" : "19-04-1991"},
            {"prompt" : "Insert user email", "name" : "email", "value" : "hola@email.com"},
            {"prompt" : "Insert user firstName", "name" : "firstname", "value" : "Mick"},
            {"prompt" : "Insert user gender", "name" : "gender", "value" : "male"},
            {"prompt" : "Insert user gender", "name" : "nickname", "value" : "gio"},
            {"prompt" : "Insert user gender", "name" : "password", "value" : "testtest"},
            {"prompt" : "Insert user gender", "name" : "balance", "value" : "0"}
        ]
        }
    } 

    (Using an existing nickname)
    "message": "There is already a user with same nickname Giovanni. 




user
----

GET: 127.0.0.1:5000/accounting/api/users/Mystery/ --> 200

	curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/users/Mystery/'

DELETE: 127.0.0.1:5000/accounting/api/users/Mystery/ --> 401

	curl -i -X DELETE \ 'http://127.0.0.1:5000/accounting/api/users/Mystery/'

DELETE: 127.0.0.1:5000/accounting/api/users/Mystery/ --> 204

	curl -i -X DELETE \   -H "Authorization:Mystery" \ 'http://127.0.0.1:5000/accounting/api/users/Mystery/'

GET: 127.0.0.1:5000/accounting/api/users/Wappu/ --> 404

	curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/users/Wappu/'

DELETE: 127.0.0.1:5000/accounting/api/users/Wappu/ --> 401

	curl -i -X DELETE \   -H "Authorization:Basic d2FwcHU6d2FwcHU=" \ 'http://127.0.0.1:5000/accounting/api/users/Wappu/'


incomes
-------

DELETE: 127.0.0.1:5000/accounting/api/user/usr-1/incomes/ --> 405

	curl -i -X DELETE \   -H "Authorization:Mystery" \ 'http://127.0.0.1:5000/accounting/api/user/usr-1/incomes/'

GET: 127.0.0.1:5000/accounting/api/user/usr-1/incomes/ --> 200

    curl -i -X GET  \ 'http://127.0.0.1:5000/accounting/api/user/usr-1/incomes/'

GET: 127.0.0.1:5000/accounting/api/user/usr-9/incomes/ --> 404

    curl -i -X GET  \ 'http://127.0.0.1:5000/accounting/api/user/usr-1/incomes/'

POST: 127.0.0.1:5000/accounting/api/user/usr-1/incomes/ --> 201

    body:
    {"template" : {
        "data" : [
            {"prompt" : "", "name" : "source", "value" : "Bike"},
            {"prompt" : "", "name" : "amount", "value" : "30"},
            {"prompt" : "", "name" : "date", "value" : "10-03-2015"},
            {"prompt" : "", "name" : "description", "value" : "Blue bike"}
                ]
                    }
    }



income
------

GET: http://127.0.0.1:5000/accounting/api/incomes/inc-1/ -- > 200

	curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/incomes/inc-1/'


GET: http://127.0.0.1:5000/accounting/api/incomes/exp-1/ --> 500 Income id is malformed

	curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/incomes/exp-1/'

DELETE: http://127.0.0.1:5000/accounting/api/incomes/inc-1/ --> 204

	curl -i -X DELETE \ 'http://127.0.0.1:5000/accounting/api/incomes/inc-1/'

DELETE: http://127.0.0.1:5000/accounting/api/incomes/inc-10/ --> 404

	curl -i -X DELETE \ 'http://127.0.0.1:5000/accounting/api/incomes/inc-10/'

PUT: http://127.0.0.1:5000/accounting/api/incomes/inc-4/
    body:

    {"template" : {
        "data" : [
            {"prompt" : "", "name" : "source", "value" : "Skates"},
            {"prompt" : "", "name" : "amount", "value" : "10"},
            {"prompt" : "", "name" : "date", "value" : "15-05-2015"},
            {"prompt" : "", "name" : "description", "value" : "Ice skates payment"}
                ]
                    }
    }

expenses
--------

GET: 127.0.0.1:5000/accounting/api/user/usr-1/expenses/ --> 200

    curl -i -X GET  \ 'http://127.0.0.1:5000/accounting/api/user/usr-1/expenses/'

GET: 127.0.0.1:5000/accounting/api/user/usr-7/expenses/ --> 404

    curl -i -X GET  \ 'http://127.0.0.1:5000/accounting/api/user/usr-7/expenses/'

DELETE: 127.0.0.1:5000/accounting/api/user/usr-1/expenses/ --> 405

    curl -i -X DELETE \   -H "Authorization:Mystery" \ 'http://127.0.0.1:5000/accounting/api/user/usr-1/expenses/'

POST: 127.0.0.1:5000/accounting/api/user/usr-1/expenses/ --> 201

    body:
    {"template" : {
        "data" : [
        {"prompt" : "", "name" : "source", "value" : "Skates"},
        {"prompt" : "", "name" : "amount", "value" : "10"},
        {"prompt" : "", "name" : "date", "value" : "15-05-2015"},
        {"prompt" : "", "name" : "description", "value" : "Ice skates payment"}
                ]
                    }
    }


expense
-------

GET: http://127.0.0.1:5000/accounting/api/expenses/exp-1/ --> 200

	curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/expenses/exp-1/'

GET: http://127.0.0.1:5000/accounting/api/expenses/exp-10/ --> 404

	curl -i -X GET \ 'http://127.0.0.1:5000/accounting/api/expenses/exp-10/'

DELETE: http://127.0.0.1:5000/accounting/api/expenses/exp-10/ --> 404

	curl -i -X DELETE \ 'http://127.0.0.1:5000/accounting/api/expenses/exp-10/'

PUT: http://127.0.0.1:5000/accounting/api/expenses/exp-4/
    body:

    {"template" : {
        "data" : [
            {"prompt" : "", "name" : "source", "value" : "Pillows"},
            {"prompt" : "", "name" : "amount", "value" : "15"},
            {"prompt" : "", "name" : "date", "value" : "10-05-2015"},
            {"prompt" : "", "name" : "description", "value" : "Pillows for the bed"}
                ]
                }
    }






