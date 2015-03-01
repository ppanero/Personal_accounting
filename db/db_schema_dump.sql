PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- -----------------------------------------------------
-- Table user
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS user (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  nickname TEXT NOT NULL UNIQUE);

-- -----------------------------------------------------
-- Table group
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS "group" (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT);

-- -----------------------------------------------------
-- Table event
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS event (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  date TEXT,
  group_id INTEGER NOT NULL,
  FOREIGN KEY (group_id)
  REFERENCES "group"(_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE);

-- -----------------------------------------------------
-- Table expense
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS expense (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  amount DOUBLE NOT NULL,
  date TEXT NOT NULL,
  description TEXT,
  bill_image BLOB,
  user_id INTEGER NOT NULL,
  event_id INTEGER,
  FOREIGN KEY (user_id)
  REFERENCES user (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
  FOREIGN KEY (event_id)
  REFERENCES event (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE);


-- -----------------------------------------------------
-- Table income
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS  income (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  amount DOUBLE NOT NULL,
  date TEXT NOT NULL,
  description TEXT,
  bill_image BLOB,
  user_id INTEGER NOT NULL,
  event_id INTEGER,
  FOREIGN KEY (user_id)
  REFERENCES user (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
  FOREIGN KEY (event_id)
  REFERENCES event (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE);


-- -----------------------------------------------------
-- Table users_of_group
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS  users_of_group (
  user__id INTEGER NOT NULL,
  group__id INTEGER NOT NULL,
  PRIMARY KEY (user__id, group__id),
  FOREIGN KEY (user__id)
  REFERENCES user (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
  FOREIGN KEY (group__id)
  REFERENCES "group" (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE);
