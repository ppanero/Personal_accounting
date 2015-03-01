-- Insert 5 users
INSERT INTO "user" VALUES(1,'Mystery');
INSERT INTO "user" VALUES(2,'HockeyFan');
INSERT INTO "user" VALUES(3,'Mogambo');
INSERT INTO "user" VALUES(4,'OptimusPrime');
INSERT INTO "user" VALUES(5,'Dickens');
-- Insert 2 groups
INSERT INTO "group" VALUES(1, 'Club 16', 'This group is for the accounting of the group of friends of YOK 16');
INSERT INTO "group" VALUES(2, 'Broken String', 'This group is for the accounting of the band named Broken String');
-- Insert 3 events: one group with 1 event, the other with 2
INSERT INTO "event" VALUES(1,'Russian trip','For the accounting of the trip in Russia','2015-01-20 19:30',1);
INSERT INTO "event" VALUES(2,'Stockholm trip','For the accounting of the trip in Stockholm','2015-02-03 18:20',1);
INSERT INTO "event" VALUES(3,'45 Special Concert','For the acounting of the 45 special material costs','2015-01-20 21:30',2);
-- Insert 3 users in each group (there is an user in both groups)
INSERT INTO "users_of_group" VALUES(1,1);
INSERT INTO "users_of_group" VALUES(2,1);
INSERT INTO "users_of_group" VALUES(3,1);
INSERT INTO "users_of_group" VALUES(4,2);
INSERT INTO "users_of_group" VALUES(5,2);
INSERT INTO "users_of_group" VALUES(3,2);
-- Insert 5 expenses divided between 2 users, Insert 3 expenses divided between 2 events
INSERT INTO "expense" VALUES(1, 'Meat', '7,89', '2015-01-20 19:30', 'Buying meat in Tokmanni', 'Null', 1, 'Null');
INSERT INTO "expense" VALUES(2, 'Chicken', '8,89', '2015-01-20 19:30', 'Buying chicken in Tokmanni', 'Null', 1, 'Null');
INSERT INTO "expense" VALUES(3, 'Fish', '5,89', '2015-01-20 19:30', 'Buying fish in Tokmanni', 'Null', 1, 'Null');
INSERT INTO "expense" VALUES(4, 'Boots', '47,89', '2015-01-20 19:30', 'Buying boots in Stockmann', 'Null', 2, 'Null');
INSERT INTO "expense" VALUES(5, 'Meat', '7,89', '2015-01-20 19:30', 'Buying meat in Tokmanni', 'Null', 2, 'Null');
INSERT INTO "expense" VALUES(6, 'Wood', '17,89', '2015-01-20 19:30', 'Wood for the bonfire', 'Null', 1, 1);
INSERT INTO "expense" VALUES(7, 'Meat', '7,89', '2015-01-20 19:30', 'Buying meat in Tokmanni for the bonfire', 'Null', 3, 1);
INSERT INTO "expense" VALUES(8, 'Marshmellows', '3', '2015-01-20 19:30', 'Buying marshmellows for the bonfire', 'Null', 2, 2);
-- Insert 3 incomes divided between 2 users, Insert 3 incomes dividede between 2 events
INSERT INTO "income" VALUES(1,'Salary', '700', '2015-01-20 19:30', 'Salary for working', 'Null', 1, 'Null');
INSERT INTO "income" VALUES(2,'Selling bike', '70', '2015-01-20 19:30', 'Money for selling the bike', 'Null', 1, 'Null');
INSERT INTO "income" VALUES(3,'Salary', '800', '2015-01-20 19:30', 'Salary for working', 'Null', 2, 'Null');
INSERT INTO "income" VALUES(4,'Mystery', '20', '2015-01-20 19:30', 'Money from Mystery', 'Null', 1, 1);
INSERT INTO "income" VALUES(5,'HockeyFan', '700', '2015-01-20 19:30', 'Money from HockeyFan', 'Null', 2, 1);
INSERT INTO "income" VALUES(6,'Mogambo', '700', '2015-01-20 19:30', 'Money from Mogambo', 'Null', 3, 2);
