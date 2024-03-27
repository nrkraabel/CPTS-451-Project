CREATE TABLE Review(
    ReviewID INT PRIMARY KEY,
    UserID VARCHAR(25) FOREIGN KEY REFERENCES [User].[UserID],
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],    Review VARCHAR(1024) NOT NULL, 
    Funny INTEGER DEFAULT 0,
    Cool INTEGER DEFAULT 0,
    Useful INTEGER DEFAULT 0,
    ReviewStars INTEGER DEFAULT 0,
    ReviewText VARCHAR(1024),
);


CREATE TABLE CheckIn(
    UserID VARCHAR(25) FOREIGN KEY REFERENCES [User].[userID],
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],
    DAY VARCHAR(10) NOT NULL,
    TIME VARCHAR(10) NOT NULL,
    AMOUNT INTEGER NOT NULL,
    PRIMARY KEY (UserID, BusinessID),
);

CREATE TABLE Business(
    BusinessID VARCHAR(25) PRIMARY KEY,
    BusinessName VARCHAR(80),
    Stars INTEGER,
    IsOpen BOOLEAN,
    PriceRange INTEGER NULL,
    ReviewRating INTEGER,
    CheckIns INTEGER,
    ReviewCount INTEGER,
    AddressID INTEGER FOREIGN KEY REFERENCES [Address].[AddressID]
);

CREATE TABLE BusinessCategory(
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],
    CategoryID INT FOREIGN KEY REFERENCES [Category].[CategoryID],
    PRIMARY KEY(BusinessID, CategoryID)
);

CREATE TABLE BusinessAttribute(
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],
    AttributeID INT FOREIGN KEY REFERENCES [Attribute].[AttributeID],
);

CREATE TABLE Attribute(
    AttributeID INT PRIMARY KEY,
    AttributeName VARCHAR(20) NOT NULL,
    AttributeValue BOOLEAN NOT NULL
);

CREATE TABLE Category (
    CategoryID INT PRIMARY KEY,
    CategoryName VARCHAR(20) NOT NULL
);

CREATE TABLE Address(
    AddressID INTEGER PRIMARY KEY,
    State CHAR(2) NOT NULL,
    City VARCHAR(20) NOT NULL,
    PostalCode CHAR(5) NOT NULL,
);