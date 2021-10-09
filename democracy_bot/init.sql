CREATE TABLE IF NOT EXISTS canadian_constituencies (
	postal_code varchar(7) PRIMARY KEY NOT NULL,
	MP varchar(255),
	MP_email varchar(255),
	constituency varchar(255),
	province varchar(32),
    county varchar(255),
    place varchar(255),
    constituency_population int,
    constituency_registered_voters int,
    constituency_polling_divisions int
);