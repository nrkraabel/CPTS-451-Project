
CREATE TABLE Business(
    BusinessID VARCHAR(25) PRIMARY KEY,
    BusinessName VARCHAR(80),
    Stars INTEGER,
    ReviewRating INTEGER,
    CheckIns INTEGER,
    ReviewCount INTEGER,
    State CHAR(2) NOT NULL,
    City VARCHAR(20) NOT NULL,
    Address VARCHAR(250) NOT NULL,
    Zipcode CHAR(5) NOT NULL
);

CREATE TABLE CheckIn(
    BusinessID VARCHAR(25) NOT NULL,
    DAY VARCHAR(10) NOT NULL,
    TIME VARCHAR(10) NOT NULL,
    AMOUNT INTEGER NOT NULL,
    FOREIGN KEY(BusinessID) REFERENCES Business(BusinessID),
    PRIMARY KEY (DAY, TIME)
);

CREATE TABLE Review(
    ReviewID SERIAL PRIMARY KEY,
    BusinessID VARCHAR(25) NOT NULL,    
    Review VARCHAR(1024) NOT NULL, 
    Funny INTEGER DEFAULT 0,
    Cool INTEGER DEFAULT 0,
    Useful INTEGER DEFAULT 0,
    ReviewStars INTEGER DEFAULT 0,
    ReviewText VARCHAR(1024),
    ReviewDate DATETIME NOT NULL,
    FOREIGN KEY(BusinessID) REFERENCES Business(BusinessID)
);

CREATE TABLE Attribute(
    AttributeID SERIAL PRIMARY KEY, -- doing this for faster queries
    AttributeName VARCHAR(40) UNIQUE NOT NULL
);

CREATE TABLE Category (
    CategoryID SERIAL PRIMARY KEY, -- Doing this for faster queries
    CategoryName VARCHAR(40) UNIQUE NOT NULL
);

CREATE TABLE BusinessCategory(
    BusinessID VARCHAR(25) not NULL,
    CategoryID SERIAL not NULL,
    FOREIGN KEY(BusinessID) REFERENCES Business(BusinessID),
    FOREIGN KEY(CategoryID) REFERENCES Category(CategoryID),
    PRIMARY KEY(BusinessID, CategoryID)
);

CREATE TABLE BusinessAttribute(
    BusinessID VARCHAR(25) NOT NULL,
    AttributeID SERIAL NOT NULL,
    AttributeFlag BOOLEAN NULL,
    AttributeValue VARCHAR(20) NULL,
    FOREIGN KEY(BusinessID) REFERENCES Business(BusinessID),
    FOREIGN KEY(AttributeID) REFERENCES Attribute(AttributeID),
    PRIMARY KEY(BusinessID, AttributeID)
);

