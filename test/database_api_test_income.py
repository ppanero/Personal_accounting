import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path


class IncomeDbAPITestCase(BaseTestCase):
    """
            The format of the income dictionary is the following:
            {'source': source, 'amount': amount,
            'date': date, 'description': description, 'income_id': income_id}
            Where:
            - source: source of the income
            - amount: monetary amount of the income
            - date: date in which the income was received
            - description: description of the income (similar to concept in bank transactions)
            - user_id: id of the user to whom the income belongs
    """
    # the strip function removes the tabs generated.
    income1_source = 'Fon salary'
    income1_amount = '1200.0'
    income1_date = '27-10-2014'
    income1_description = 'Monthly salary for working in fon technologies'
    income1_user_id = 'usr-1'
    income1_id = 'inc-1'
    income1 = {'_id': income1_id, 'source': income1_source, 'amount': income1_amount,
               'date': income1_date, 'description': income1_description, 'user_id': income1_user_id}
    income1_source_modified = 'Pragsis salary'
    income1_description_modified = 'Monthly salary for working in Pragsis Technologies'
    modified_income1 = {'_id': income1_id, 'source': income1_source_modified, 'amount': income1_amount,
                        'date': income1_date, 'description': income1_description_modified, 'user_id': income1_user_id}
    new_income_id = 'inc-2'
    new_income = {'_id': new_income_id, 'source': income1_source, 'amount': income1_amount,
                  'date': income1_date, 'description': income1_description, 'user_id': income1_user_id}
    no_income_id = 'inc-10'
    initial_size = 1

    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__

    def test_income_table_created(self):
        """
        Checks that the table initially contains 1 incomes (check
        forum_data_dump.sql)
        """
        print '(' + self.test_income_table_created.__name__ + ')', \
            self.test_income_table_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM income'
        # Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            # Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Provide support for foreign keys
            cur.execute(keys_on)
            # Execute main SQL Statement
            cur.execute(query1)
            incomes = cur.fetchall()
            # Assert
            self.assertEquals(len(incomes), self.initial_size)
        if con:
            con.close()

    def test_get_income(self):
        """
        Test get_income with id Mystery and HockeyFan
        """
        print '(' + self.test_get_income.__name__ + ')', \
            self.test_get_income.__doc__
        # Test with an existing income
        income = db.get_income(self.income1_id)
        self.assertDictContainsSubset(income, self.income1)

    def test_get_income_noexistingid(self):
        print '(' + self.test_get_income_noexistingid.__name__ + ')', \
            self.test_get_income_noexistingid.__doc__
        # Test with an existing income
        income = db.get_income(self.no_income_id)
        self.assertIsNone(income)

    def test_delete_income(self):
        """
        Test that the income Mystery is deleted
        """
        print '(' + self.test_delete_income.__name__ + ')', \
            self.test_delete_income.__doc__
        resp = db.delete_income(self.income1_id)
        self.assertTrue(resp)
        # Check that the incomes has been really deleted through a get
        resp2 = db.get_income(self.income1_id)
        self.assertIsNone(resp2)

    def test_delete_income_noexistingid(self):
        """
        Test delete_income with  Batty (no-existing)
        """
        print '(' + self.test_delete_income_noexistingid.__name__ + ')', \
            self.test_delete_income_noexistingid.__doc__
        # Test with an existing income
        resp = db.delete_income(self.no_income_id)
        self.assertFalse(resp)

    def test_modify_income(self):
        """
        Test that the income Mystery is modifed
        """
        print '(' + self.test_modify_income.__name__ + ')', \
            self.test_modify_income.__doc__
        # Get the modified income
        resp = db.modify_income(self.income1_id, self.income1_source_modified, self.income1_amount, self.income1_date,
                                self.income1_description_modified)
        self.assertEquals(resp, self.income1_id)

    def test_modify_income_noexistingid(self):
        """
        Test modify_income with  income Batty (no-existing)
        """
        print '(' + self.test_modify_income_noexistingid.__name__ + ')', \
            self.test_modify_income_noexistingid.__doc__
        # Test with an existing income
        resp = db.modify_income(self.no_income_id, self.income1_source_modified, self.income1_amount, self.income1_date,
                                self.income1_description_modified)
        self.assertIsNone(resp)

    def test_create_income(self):
        """
        Test that I can add new incomes
        """
        print '(' + self.test_create_income.__name__ + ')', \
            self.test_create_income.__doc__
        id = db.create_income(self.income1_source, self.income1_amount, self.income1_date,
                              self.income1_description, self.income1_user_id)
        self.assertIsNotNone(id)
        self.assertEquals(id, self.new_income_id)

    """
    The case of creating an exiting income is not tested, because an income can be created multiple times for the same user.
    """


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
