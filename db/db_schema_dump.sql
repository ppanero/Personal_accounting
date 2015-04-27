PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- -----------------------------------------------------
-- Table user
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS user (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  nickname TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  'name' TEXT NOT NULL,
  balance REAL NOT NULL,
  birthday TEXT,
  gender TEXT);

-- -----------------------------------------------------
-- Table expense
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS expense (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  amount REAL NOT NULL,
  'date' TEXT NOT NULL,
  description TEXT,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id)
  REFERENCES user (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE);


-- -----------------------------------------------------
-- Table income
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS  income (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  amount REAL NOT NULL,
  'date' TEXT NOT NULL,
  description TEXT,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id)
  REFERENCES user (_id)
  ON DELETE CASCADE
  ON UPDATE CASCADE);

COMMIT;
PRAGMA foreign_keys=ON;