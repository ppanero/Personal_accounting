import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path


class UserDbAPITestCase(BaseTestCase):
    """
            The format of the User dictionary is the following:
            {'nickname': nickname, 'email': email,
            'password': password, 'name': name, 'balance': balance,
            'birthday': birthday, 'gender': gender}
            Where:
            - nickname: nickname of the user
            - email: electronic mail address of the user
            - password: password of the user
            - name: name of the user
            - balance: monetary balance of the user account
            - birthday: birthday date of the user
            - gender: gender of the user
    """
    # the strip function removes the tabs generated.
    user1_nickname = 'Mystery'
    user1_email = 'mystery@mystery.com'
    user1_password = 'myspass'
    user1_name = 'Miikka'
    user1_balance = '1400.0'
    user1_birthday = '20-05-1992'
    user1_gender = 'Male'
    user1_modified_nickname = 'Mystery_mod'
    user1_id = 'usr-1'
    user1 = {'user_id': user1_id,'nickname': user1_nickname, 'email': user1_email,
             'password': user1_password, 'name': user1_name, 'balance': user1_balance,
             'birthday': user1_birthday, 'gender': user1_gender}
    modified_user1 = {'user_id': user1_id,'nickname': user1_modified_nickname, 'email': user1_email,
                      'password': user1_password, 'name': user1_name, 'balance': user1_balance,
                      'birthday': user1_birthday, 'gender': user1_gender}
    new_user_id = 'usr-2'
    new_user_nickname = 'newbie'
    new_user = {'user_id': new_user_id, 'nickname': new_user_nickname, 'email': user1_email,
                'password': user1_password, 'name': user1_name, 'balance': user1_balance,
                'birthday': user1_birthday, 'gender': user1_gender}

    no_user_nickname = 'no_user'
    no_user_id = 'usr-10'
    initial_size = 1

    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__

    def test_users_table_created(self):
        """
        Checks that the table initially contains 1 users (check
        forum_data_dump.sql)
        """
        print '(' + self.test_users_table_created.__name__ + ')', \
            self.test_users_table_created.__doc__
        # Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM user'
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
            users = cur.fetchall()
            # Assert
            self.assertEquals(len(users), self.initial_size)
        if con:
            con.close()

    def test_get_user(self):
        """
        Test get_user with id Mystery and HockeyFan
        """
        print '(' + self.test_get_user.__name__ + ')', \
            self.test_get_user.__doc__
        # Test with an existing user
        user = db.get_user(self.user1_nickname)
        self.assertDictContainsSubset(user, self.user1)

    def test_get_user_noexistingnickname(self):
        print '(' + self.test_get_user_noexistingnickname.__name__ + ')', \
            self.test_get_user_noexistingnickname.__doc__
        # Test with an existing user
        user = db.get_user(self.no_user_nickname)
        self.assertIsNone(user)

    def test_delete_user(self):
        """
        Test that the user Mystery is deleted
        """
        print '(' + self.test_delete_user.__name__ + ')', \
            self.test_delete_user.__doc__
        resp = db.delete_user(self.user1_nickname)
        self.assertTrue(resp)
        # Check that the users has been really deleted through a get
        resp2 = db.get_user(self.user1_nickname)
        self.assertIsNone(resp2)
        # Check that the user does not have associated any incomes or expenses
        resp3 = db.get_user_incomes(userId=self.user1_id)
        self.assertEquals(len(resp3), 0)
        resp4 = db.get_user_expenses(userId=self.user1_id)
        self.assertEquals(len(resp4), 0)

    def test_delete_user_noexistingnickname(self):
        """
        Test delete_user with  Batty (no-existing)
        """
        print '(' + self.test_delete_user_noexistingnickname.__name__ + ')', \
            self.test_delete_user_noexistingnickname.__doc__
        # Test with an existing user
        resp = db.delete_user(self.no_user_nickname)
        self.assertFalse(resp)

    def test_modify_user(self):
        """
        Test that the user Mystery is modifed
        """
        print '(' + self.test_modify_user.__name__ + ')', \
            self.test_modify_user.__doc__
        # Get the modified user
        resp = db.modify_user(self.user1_id, self.user1_modified_nickname, self.user1_email, self.user1_name,
                              self.user1_balance, self.user1_birthday, self.user1_gender)
        self.assertEquals(resp, self.user1_id)

    def test_modify_user_noexistingid(self):
        """
        Test modify_user with  user Batty (no-existing)
        """
        print '(' + self.test_modify_user_noexistingid.__name__ + ')', \
            self.test_modify_user_noexistingid.__doc__
        # Test with an existing user
        resp = db.modify_user(self.no_user_id, self.no_user_nickname, self.user1_email, self.user1_name,
                              self.user1_balance, self.user1_birthday, self.user1_gender)
        self.assertIsNone(resp)

    def test_create_user(self):
        """
        Test that I can add new users
        """
        print '(' + self.test_create_user.__name__ + ')', \
            self.test_create_user.__doc__
        nickname = db.create_user(self.new_user_nickname, self.user1_email,
                                  self.user1_password, self.user1_name, self.user1_birthday, self.user1_gender)
        self.assertIsNotNone(nickname)
        self.assertEquals(nickname, self.new_user_nickname)

    def test_create_existing_user(self):
        """
        Test that I cannot add two users with the same name
        """
        print '(' + self.test_create_existing_user.__name__ + ')', \
            self.test_create_existing_user.__doc__
        nickname = db.create_user(self.user1_nickname, self.user1_email,
                                  self.user1_password, self.user1_name, self.user1_birthday, self.user1_gender)
        self.assertIsNone(nickname)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
