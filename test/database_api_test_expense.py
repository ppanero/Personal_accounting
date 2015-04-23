import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path


class expenseDbAPITestCase(BaseTestCase):
    """
            The format of the expense dictionary is the following:
            {'source': source, 'amount': amount,
            'date': date, 'description': description, 'expense_id': expense_id}
            Where:
            - source: source of the expense
            - amount: monetary amount of the expense
            - date: date in which the expense was received
            - description: description of the expense (similar to concept in bank transactions)
            - user_id: id of the user to whom the expense belongs
    """
    expense1_source = 'Food'
    expense1_amount = '30.74'
    expense1_date = '10-08-2014'
    expense1_description = 'Bought food at tokmanni'
    expense1_user_id = 'usr-1'
    expense1_id = 'exp-1'
    expense1 = {'_id': expense1_id, 'source': expense1_source, 'amount': expense1_amount,
               'date': expense1_date, 'description': expense1_description, 'user_id': expense1_user_id}
    expense1_source_modified = 'Skates'
    expense1_description_modified = 'Bought ice skates at intersport'
    modified_expense1 = {'_id': expense1_id, 'source': expense1_source_modified, 'amount': expense1_amount,
                        'date': expense1_date, 'description': expense1_description_modified, 'user_id': expense1_user_id}
    new_expense_id = 'exp-2'
    new_expense = {'_id': new_expense_id, 'source': expense1_source, 'amount': expense1_amount,
                  'date': expense1_date, 'description': expense1_description, 'user_id': expense1_user_id}
    no_expense_id = 'exp-10'
    initial_size = 1

    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__

    def test_expense_table_created(self):
        """
        Checks that the table initially contains 1 expenses (check
        forum_data_dump.sql)
        """
        print '(' + self.test_expense_table_created.__name__ + ')', \
            self.test_expense_table_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM expense'
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
            expenses = cur.fetchall()
            # Assert
            self.assertEquals(len(expenses), self.initial_size)
        if con:
            con.close()

    def test_get_expense(self):
        """
        Test get_expense with id Mystery and HockeyFan
        """
        print '(' + self.test_get_expense.__name__ + ')', \
            self.test_get_expense.__doc__
        # Test with an existing expense
        expense = db.get_expense(self.expense1_id)
        self.assertDictContainsSubset(expense, self.expense1)

    def test_get_expense_noexistingid(self):
        print '(' + self.test_get_expense_noexistingid.__name__ + ')', \
            self.test_get_expense_noexistingid.__doc__
        # Test with an existing expense
        expense = db.get_expense(self.no_expense_id)
        self.assertIsNone(expense)

    def test_delete_expense(self):
        """
        Test that the expense Mystery is deleted
        """
        print '(' + self.test_delete_expense.__name__ + ')', \
            self.test_delete_expense.__doc__
        resp = db.delete_expense(self.expense1_id)
        self.assertTrue(resp)
        # Check that the expenses has been really deleted through a get
        resp2 = db.get_expense(self.expense1_id)
        self.assertIsNone(resp2)

    def test_delete_expense_noexistingid(self):
        """
        Test delete_expense with  Batty (no-existing)
        """
        print '(' + self.test_delete_expense_noexistingid.__name__ + ')', \
            self.test_delete_expense_noexistingid.__doc__
        # Test with an existing expense
        resp = db.delete_expense(self.no_expense_id)
        self.assertFalse(resp)

    def test_modify_expense(self):
        """
        Test that the expense Mystery is modifed
        """
        print '(' + self.test_modify_expense.__name__ + ')', \
            self.test_modify_expense.__doc__
        # Get the modified expense
        resp = db.modify_expense(self.expense1_id, self.expense1_source_modified, self.expense1_amount, self.expense1_date,
                                self.expense1_description_modified)
        self.assertEquals(resp, self.expense1_id)

    def test_modify_expense_noexistingid(self):
        """
        Test modify_expense with  expense Batty (no-existing)
        """
        print '(' + self.test_modify_expense_noexistingid.__name__ + ')', \
            self.test_modify_expense_noexistingid.__doc__
        # Test with an existing expense
        resp = db.modify_expense(self.no_expense_id, self.expense1_source_modified, self.expense1_amount, self.expense1_date,
                                self.expense1_description_modified)
        self.assertIsNone(resp)

    def test_create_expense(self):
        """
        Test that I can add new expenses
        """
        print '(' + self.test_create_expense.__name__ + ')', \
            self.test_create_expense.__doc__
        id = db.create_expense(self.expense1_source, self.expense1_amount, self.expense1_date,
                              self.expense1_description, self.expense1_user_id)
        self.assertIsNotNone(id)
        self.assertEquals(id, self.new_expense_id)

    """
    The case of creating an exiting expense is not tested, because an expense can be created multiple times for the same user.
    """


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
