__author__ = 'Pablo Panero'
__author__ = 'Raúl Jiménez Redondo'

import sqlite3, sys, re, os
# Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/accounting_db.db'
DEFAULT_SCHEMA = "db/db_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/db_data_dump.sql"


class AccountingDatabase(object):
    """
    API to access Accounting database.
    """

    def __init__(self, db_path=None):
        """
        db_path is the address of the path with respect to the calling script.
        If db_path is None, DEFAULT_DB_PATH is used instead.
        """
        super(AccountingDatabase, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    # Setting up the database. Used for the tests.
    # SETUP, POPULATE and DELETE the database
    def clean(self):
        """
        Purge the database removing old values.
        """
        os.remove(self.db_path)

    def load_init_values(self, schema=None, dump=None):
        """
        Create the database and populate it with initial values. The schema
        argument defines the location of the schema sql file while the dump
        argument defines the location of the data dump sql file. If no value
        is provided default values are defined by the global variables
        DEFAULT_SCHEMA and DEFAULT_DATA_DUMP
        """
        self.create_tables_from_schema(schema)
        self.load_table_values_from_dump(dump)

    def create_tables_from_schema(self, schema=None):
        """
        Create programmatically the tables from a schema file.
        schema contains the path to the .sql schema file. If it is None,
        DEFAULT_SCHEMA is used instead.
        """
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        with open(schema) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    def load_table_values_from_dump(self, dump=None):
        """
        Populate programmatically the tables from a dump file.
        dump is the  path to the .sql dump file. If it is None,
        DEFAULT_DATA_DUMP is used instead.
        """
        con = sqlite3.connect(self.db_path)
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open(dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    # CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def create_user_table(self):
        """
        Create the table user programmatically without using .sql file.
        Print an error message in the console if it could not be created.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE user (_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    nickname TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, \
                    password TEXT NOT NULL, name TEXT NOT NULL, balance REAL NOT NULL, \
                    birthday TEXT, gender TEXT)'

        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None

    def create_expense_table(self):
        """
        Create the table expense programmatically without using .sql file.
        Print an error message in the console if it could not be created.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE expense(_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    source TEXT NOT NULL, amount REAL NOT NULL, \
                    date TEXT NOT NULL, description TEXT, \
                    user_id INTEGER NOT NULL, \
                    FOREIGN KEY(user_id) REFERENCES user (_id) \
                    ON DELETE CASCADE ON UPDATE CASCADE)'

        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None

    def create_income_table(self):
        """
        Create the table income programmatically without using .sql file.
        Print an error message in the console if it could not be created.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE income(_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    source TEXT NOT NULL, amount REAL NOT NULL, \
                    date TEXT NOT NULL, description TEXT, \
                    user_id INTEGER NOT NULL, \
                    FOREIGN KEY(user_id) REFERENCES user (_id) \
                    ON DELETE CASCADE ON UPDATE CASCADE)'
        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None

    def create_all_tables(self):
        """
        Create all tables programmatically, without using an external sql.
        It prints error messages in console if any of the tables could not be
        created.
        """
        self.create_user_table()
        self.create_expense_table()
        self.create_income_table()

    # HELPERS
    def check_foreign_keys_status(self):
        """
        Check if the foreign keys has been activated. Return and print in the
        screen if foreign keys are activated.
        """
        con = None
        try:
            # Connects to the database.
            con = sqlite3.connect(self.db_path)
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            # Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            # We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            data_text = 'ON' if data == (1,) else 'OFF'
            print "Foreign Keys status: %s" % data_text

        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            sys.exit(1)

        finally:
            if con:
                con.close()
        return data

    def set_and_check_foreign_keys_status(self):
        """
        Activate the support for foreign keys and later check that the support
        exists. Print the results of this test.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        con = None
        try:
            # connects to the database.
            con = sqlite3.connect(self.db_path)
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            # execute the pragma command, ON
            cur.execute(keys_on)
            # execute the pragma check command
            cur.execute('PRAGMA foreign_keys')
            # we know we retrieve just one record: use ftchone()
            data = cur.fetchone()
            data_text = 'ON' if data == (1,) else 'OFF'
            print "Foreign Keys status: %s" % data_text

        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            sys.exit(1)

        finally:
            if con:
                con.close()
        return data

    # ACCESSING THE USER TABLE
    # Here the helpers that transform database rows into dictionary.
    def _create_user_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.
        Dictionary contains the following keys:
          - userid: id of the user (int)
          - nickname: user's nickname
        Note that all values in the returned dictionary are string unless
        otherwise stated.
        """
        id = 'usr-' + str(row['user_id'])
        nickname = row['nickname']
        email = row['email']
        password = row['password']
        name = row['name']
        balance = str(row['balance'])
        birthday = row['birthday']
        gender = row['gender']

        user = {'user_id': id, 'nickname': nickname, 'email': email,
                'password': password, 'name': name, 'balance': balance,
                'birthday': birthday, 'gender': gender}
        return user

    # User Table API.
    def get_user(self, userId):
        """
        Return an user with id equals userid or None if there is no
        such user.
        OUTPUT:
            - The returned value is a dictionary with the same format as
              described in _create_user_object.
        INPUT:
            - The id of the user. Note that userid is a string.
        """
        # Changes the id to integer
        match = re.match(r'usr-(\d{1,3})', userId)
        if match is None:
            raise ValueError("The user id is malformed")
        userid = int(match.group(1))

        # Create the SQL Query
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM user WHERE _id = ?'
        # Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (userid,)
            cur.execute(query, pvalue)
            # Process the response.
            # Just one row is expected
            row = cur.fetchone()
            if row is None:
                return None
            # Build the return object
            return self._create_user_object(row)

    def delete_user(self, userId):
        """
        Delete the user with id given as parameter.
        INPUT:
            The id of the user to remove. Note that userid is a string.
        OUTPUT:
             True if the user has been deleted, False otherwise.
        """
        # Changes the id to integer
        match = re.match(r'usr-(\d{1,3})', userId)
        if match is None:
            raise ValueError("The user id is malformed")
        userid = int(match.group(1))

        # Create the SQL statment
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'DELETE FROM user WHERE _id = ?'
        # connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (userid,)
            cur.execute(stmnt, pvalue)
            # Check that the user has been deleted
            if cur.rowcount < 1:
                return False
            # Return true if user is deleted.
            return True

    def modify_user(self, userId, nickname, email, name, balance, birthday, gender):
        """
        Modify the nickname, of the user which has userId as id.
        INPUT:
            - userId: The id of the user to change nickname.
            - nickname: the new nickname for the user with userId as id.
        OUTPUT:
            - returns the id of the edited user or None if the user was
              not found.
        """
        # Changes the id to integer
        match = re.match(r'usr-(\d{1,3})', userId)
        if match is None:
            raise ValueError("The user id is malformed")
        userid = int(match.group(1))

        # Create the SQL statment
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE user SET nickname=? , email=? , name=?, ' \
                'balance=? , birthday=? , gender=? WHERE _id = ?'
        # Connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (nickname, email, name, balance, birthday, gender, userid)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return None
            return userId

    def create_user(self, nickname, email, password, name, birthday, gender):
        """
        Create a new user with the data provided as arguments.
        INPUT:
            - nickname: nickname for the new user
        Note that all values are string if they are not otherwise indicated.
        OUTPUT:
            - returns the id of the created user or None if the user. None if the
            nickname is already in use.
        raises AccountingDatabaseError if the database could not be modified.
        """

        # Create the SQL statment
        # SQL STATMENTS FOR KEYS
        keys_on = 'PRAGMA foreign_keys = ON'
        # SQL to test that the nickname is not in use
        query1 = 'SELECT * from user WHERE nickname = ?'
        # SQL Statement for getting the user id given a nickname
        stmnt = 'INSERT INTO user (nickname, email, password, name, balance, ' \
                'birthday, gender) VALUES (?, ?, ?, ?, ?, ?, ?)'

        # Connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # If the nickname exists return None
            pvalue = (nickname,)
            cur.execute(query1, pvalue)
            messages = cur.fetchall()
            if len(messages) < 1:
                return None

            # Execute the statement
            pvalue = (nickname, email, password, name, 0, birthday, gender)
            cur.execute(stmnt, pvalue)
            # Extract the id of the added user
            lid = cur.lastrowid
            # Return the id in
            return str(lid) if lid is not None else None

    # ACCESSING THE INCOME TABLE
    # Here the helpers that transform database rows into dictionary.
    def _create_income_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.
        Dictionary contains the following keys:
          - income_id: id of the income (int)
          - source: income's surce text
          - amount: income's amount (REAL)
          - description: income's description
          - user_id: income's user
          - event_id: income's event
          - date: income's date

        """
        income_id = 'inc-' + str(row['_id'])
        income_user_id = 'inc-' + str(row['user_id'])
        income_source = row['source']
        income_amount = str(row['amount'])
        income_description = row['description']
        income_date = row['date']
        income = {'income_id': income_id, 'user': income_user_id,
                  'source': income_source, 'amount': income_amount,
                  'description': income_description, 'date': income_date}
        return income

    def _create_income_list_object(self, row):
        """
        Same as _create_income_object. However, the result of this method is
        targeted to create lists. The only keys returned by the objects
        are income_id, source, amount and date.
        """
        item_id = 'inc-' + str(row['item_id'])
        item_source = row['source']
        item_amount = row['amount']
        item_date = row['date']
        item = {'income_id': item_id, 'source': item_source,
                'amount': item_amount, 'date': item_date}
        return item

    def get_income(self, incomeId):
        """
        Return a income with id equals income or None if there is no
        such income.
        OUTPUT:
            - The returned value is a dictionary with the same format as
              described in _create_income_object.
        INPUT:
            - The id of the income. Note that incomeid is a string with
              format itm-\d{1,3}.
        Raises a value error if incomeid is not well formed.
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'inc-(\d{1,3})', incomeId)
        if match is None:
            raise ValueError("The incomeid is malformed")
        incomeid = int(match.group(1))

        # Create the SQL Query
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM income WHERE _id = ?'
        # Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (incomeid,)
            cur.execute(query, pvalue)
            # Process the response.
            # Just one row is expected
            row = cur.fetchone()
            if row is None:
                return None
            # Build the return object
            return self._create_income_object(row)

    def get_user_incomes(self, userId):
        """
        Return a list of all the messages sent by:
            * The user with nick equals to nickname (string)
            * All the users in the system if nickname is None
        Before returning it the list is filtered accordding to the arguments:
            * number_of_messages (int): sets the maximum lenght of the list
              (-1 means no limit)
            * before (long integer): All timestamps > before (UNIX timestamps)
                                     are removed
            * after (long integer): All timestamps < after (UNIX timestamp)
                                    are removed

        Each message in the list is a dictionary containing the following keys:
         - messageid: string with the format msg-\d{1,3}. Id of the message.
         - sender: nickname of the message's author,
         - title: string containing the title of the message
         - timestamp: UNIX timestamp (long int) that specifies when the message
                    was created.
        Note that all values in the returned dictionary are string unless
        otherwise stated.
        raises a ValueError if the before or after are not valid data formats
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'usr-(\d{1,3})', userId)
        if match is None:
            raise ValueError("The user id is malformed")
        userid = int(match.group(1))

        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        # Query to check the existance of the user
        # Might not be needed, but by using it we can distinguish no
        # user from no income when user exists
        query1 = 'SELECT * FROM user WHERE _id = ?'
        # SQL statement to get incomes
        stmnt = 'SELECT * FROM incomes WHERE user_id = ?'

        # Connects to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (userid,)
            cur.execute(query1, pvalue)
            # Get results
            rows = cur.fetchall()
            if len(rows) < 1:
                return None
            cur.execute(stmnt, pvalue)
            rows = cur.fetchall()
            # Build the return object
            incomes = []
            for row in rows:
                income = self._create_message_list_object(row)
                incomes.append(income)
            return incomes

    def delete_income(self, incomeId):
        """
        Delete the income with id given as parameter.
        INPUT:
            The id of the user to remove. Note that userid is a string.
        OUTPUT:
             True if the user has been deleted, False otherwise.
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'inc-(\d{1,3})', incomeId)
        if match is None:
            raise ValueError("The income id is malformed")
        incomeid = int(match.group(1))

        # Create the SQL statment
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'DELETE FROM income WHERE _id = ?'
        # connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (incomeid,)
            cur.execute(stmnt, pvalue)
            # Check that the user has been deleted
            if cur.rowcount < 1:
                return False
            # Return true if user is deleted.
            return True

    def modify_income(self, incomeId, source, amount, date, description):
        """
        Modify the nickname, of the user which has userId as id.
        INPUT:
            - incomeId: The id of the inocome to change values.
            - source, amount, date, and description are the new values for the
            fileds names accordingly.

        OUTPUT:
            - returns the id of the edited income or None if the user was
              not found.
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'inc-(\d{1,3})', incomeId)
        if match is None:
            raise ValueError("The incomeid is malformed")
        incomeid = int(match.group(1))

        # Create the SQL statment
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE income SET source=?, amount=?, date=?, description=?  WHERE _id = ?'
        # Connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (source, amount, date, description, incomeid)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return None
            return 'inc-' + str(incomeid)

    def create_income(self, source, amount, date, description, userid):
        """
        Create a new user with the data provided as arguments.
        INPUT:
            - source, amount, date, description, bill_image are the
            values for the fields named accordingly.
            - user_id: id of the user that creates the income.
            - event_id: id of the event for which the income is done.
        Note that all values are string if they are not otherwise indicated.
        OUTPUT:
            - returns the id of the created income. None if the user or event
            does not exists.
        raises AccountingDatabaseError if the database could not be modified.
        """

        # Create the SQL statment
        # SQL STATMENTS FOR KEYS
        keys_on = 'PRAGMA foreign_keys = ON'
        # SQL to test that the user exists
        query1 = 'SELECT * from user WHERE _id = ?'
        # SQL Statement for getting the user id given a nickname
        stmnt = 'INSERT INTO income (source, amount, date, description, ' \
                'user_id) VALUES (?, ?, ?, ?, ?)'

        # Connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)

            # Execute SQL Statement to check if the user exists
            pvalue = (userid,)
            cur.execute(query1, pvalue)
            row = cur.fetchone()
            if row is None:
                return None

            # If the nickname exists return None
            pvalue = (source, amount, date, description,
                      userid)
            cur.execute(stmnt, pvalue)
            messages = cur.fetchall()
            if len(messages) < 1:
                return None

            # Execute the statement
            cur.execute(stmnt, pvalue)
            # Extract the id of the added message
            lid = cur.lastrowid
            # Return the id in
            return str(lid) if lid is not None else None

    # ACCESSING THE EXPENSE TABLE
    # Here the helpers that transform database rows into dictionary.
    def _create_expense_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.
        Dictionary contains the following keys:
          - expense_id: id of the expense (int)
          - source: expense's surce text
          - amount: expense's amount (REAL)
          - description: expense's description
          - user_id: expense's user
          - event_id: expense's event
          - date: expense's date

        """
        expense_id = 'exp-' + str(row['_id'])
        expense_user_id = 'usr-' + str(row['user_id'])
        expense_source = row['source']
        expense_amount = row['amount']
        expense_description = row['description']
        expense_date = row['date']
        expense = {'expense_id': expense_id, 'user': expense_user_id,
                   'source': expense_source, 'amount': expense_amount,
                   'description': expense_description, 'date': expense_date}
        return expense

    def _create_expense_list_object(self, row):
        """
        Same as _create_expense_object. However, the result of this method is
        targeted to create lists. The only keys returned by the objects
        are income_id, source, amount and date.
        """
        expense_id = 'exp-' + str(row['_id'])
        expense_source = row['source']
        expense_amount = row['amount']
        expense_date = row['date']
        expense = {'expense_id': expense_id, 'source': expense_source,
                'amount': expense_amount, 'date': expense_date}
        return expense

    def get_expense(self, expenseId):
        """
        Return a expense with id equals expense or None if there is no
        such expense.
        OUTPUT:
            - The returned value is a dictionary with the same format as
              described in _create_expense_object.
        INPUT:
            - The id of the expense. Note that expenseid is a string with
              format itm-\d{1,3}.
        Raises a value error if expenseid is not well formed.
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'exp-(\d{1,3})', expenseId)
        if match is None:
            raise ValueError("The expenseid is malformed")
        expenseid = int(match.group(1))

        # Create the SQL Query
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM expense WHERE _id = ?'
        # Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (expenseid,)
            cur.execute(query, pvalue)
            # Process the response.
            # Just one row is expected
            row = cur.fetchone()
            if row is None:
                return None
            # Build the return object
            return self._create_expense_object(row)

    def get_user_expenses(self, userId):
        """
        Return a list of all the messages sent by:
            * The user with nick equals to nickname (string)
            * All the users in the system if nickname is None
        Before returning it the list is filtered accordding to the arguments:
            * number_of_messages (int): sets the maximum lenght of the list
              (-1 means no limit)
            * before (long integer): All timestamps > before (UNIX timestamps)
                                     are removed
            * after (long integer): All timestamps < after (UNIX timestamp)
                                    are removed

        Each message in the list is a dictionary containing the following keys:
         - messageid: string with the format msg-\d{1,3}. Id of the message.
         - sender: nickname of the message's author,
         - title: string containing the title of the message
         - timestamp: UNIX timestamp (long int) that specifies when the message
                    was created.
        Note that all values in the returned dictionary are string unless
        otherwise stated.
        raises a ValueError if the before or after are not valid data formats
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'usr-(\d{1,3})', userId)
        if match is None:
            raise ValueError("The user id is malformed")
        userid = int(match.group(1))
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        # Query to check the existance of the user
        # Might not be needed, but by using it we can distinguish no
        # user from no income when user exists
        query1 = 'SELECT * FROM user WHERE _id = ?'
        # SQL statement to get expenses
        stmnt = 'SELECT * FROM expense WHERE user_id = ?'

        # Connects to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (userid,)
            cur.execute(query1, pvalue)
            # Get results
            rows = cur.fetchall()
            if len(rows) < 1:
                return None
            cur.execute(stmnt, pvalue)
            rows = cur.fetchall()
            # Build the return object
            expenses = []
            for row in rows:
                expense = self._create_expense_list_object(row)
                expenses.append(expense)
            return expenses

    def delete_expense(self, expenseId):
        """
        Delete the income with id given as parameter.
        INPUT:
            The id of the user to remove. Note that userid is a string.
        OUTPUT:
             True if the user has been deleted, False otherwise.
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'exp-(\d{1,3})', expenseId)
        if match is None:
            raise ValueError("The expense id is malformed")
        expenseid = int(match.group(1))

        # Create the SQL statment
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'DELETE FROM expense WHERE _id = ?'
        # connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (expenseid,)
            cur.execute(stmnt, pvalue)
            # Check that the user has been deleted
            if cur.rowcount < 1:
                return False
            # Return true if user is deleted.
            return True

    def modify_expense(self, expenseId, source, amount, date, description):
        """
        Modify the nickname, of the user which has userId as id.
        INPUT:
            - incomeId: The id of the inocome to change values.
            - source, amount, date, and description are the new values for the
            fileds names accordingly.

        OUTPUT:
            - returns the id of the edited income or None if the user was
              not found.
        """
        # Extracts the int which is the id for a message in the database
        match = re.match(r'exp-(\d{1,3})', expenseId)
        if match is None:
            raise ValueError("The expense id is malformed")
        expenseid = int(match.group(1))

        # Create the SQL statment
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'UPDATE expense SET source=?, amount=?, date=?, description=?  WHERE _id = ?'
        # Connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            pvalue = (source, amount, date, description, expenseid)
            cur.execute(stmnt, pvalue)
            if cur.rowcount < 1:
                return None
            return 'exp-' + str(expenseid)

    def create_expense(self, source, amount, date, description, userid):
        """
        Create a new user with the data provided as arguments.
        INPUT:
            - source, amount, date, description, bill_image are the
            values for the fields named accordingly.
            - user_id: id of the user that creates the income.
            - event_id: id of the event for which the income is done.
        Note that all values are string if they are not otherwise indicated.
        OUTPUT:
            - returns the id of the created income. None if the user or event
            does not exists.
        raises AccountingDatabaseError if the database could not be modified.
        """

        # Create the SQL statement
        # SQL STATEMENTS FOR KEYS
        keys_on = 'PRAGMA foreign_keys = ON'
        # SQL to test that the user exists
        query1 = 'SELECT * from user WHERE _id = ?'
        # SQL Statement for getting the user id given a nickname
        stmnt = 'INSERT INTO expense (source, amount, date, description, ' \
                'user_id) VALUES (?, ?, ?, ?, ?)'
        # Connects  to the database.
        con = sqlite3.connect(self.db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute SQL Statement to check if the user exists
            pvalue = (userid,)
            cur.execute(query1, pvalue)
            row = cur.fetchone()
            if row is None:
                return None

            # If the nickname exists return None
            pvalue = (source, amount, date, description,
                      userid)
            cur.execute(stmnt, pvalue)
            messages = cur.fetchall()
            if len(messages) < 1:
                return None

            # Execute the statement
            cur.execute(stmnt, pvalue)
            # Extract the id of the added message
            lid = cur.lastrowid
            # Return the id in
            return str(lid) if lid is not None else None