CREATE TABLE Users (
	uid SERIAL PRIMARY KEY,
	email VARCHAR(50) UNIQUE NOT NULL,
	name VARCHAR(50) NOT NULL,
	hash VARCHAR(256) NOT NULL,
	salt VARCHAR(128) NOT NULL
);

CREATE TABLE Managers(
	uid INTEGER PRIMARY KEY,
	FOREIGN KEY (uid) REFERENCES Users(uid)
		ON DELETE CASCADE
);

CREATE TABLE Entities(
	eid SERIAL PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	location VARCHAR(100),
	title VARCHAR(50),
	picture_filename VARCHAR(100)
);

CREATE TABLE Appointments(
	aid SERIAL PRIMARY KEY,
	uid INTEGER NOT NULL,
	eid INTEGER NOT NULL,
	description VARCHAR(100),
	datetime_start timestamp,
	datetime_end timestamp,
	FOREIGN KEY (uid) REFERENCES Users(uid),
	FOREIGN KEY (eid) REFERENCES Entities(eid)
);
