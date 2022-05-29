DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews ( 
    ID TEXT NOT NULL CHECK(ID != ''),
	Country TEXT NOT NULL, --additional checks are done in app.py
    Brand TEXT NOT NULL CHECK(Brand != ''),
	Type TEXT CHECK(Type != ''),
    Package TEXT CHECK(Package != ''),
	Rating REAL NOT NULL CHECK(Rating >= 0.0 AND Rating<=5.0)
); -- this is a rowid table, therefore column id from the sample dataset need not be used as the primary key and I can import all rows of the data into the table