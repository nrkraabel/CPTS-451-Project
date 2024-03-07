CREATE TABLE User (
    UserID VARCHAR(25) PRIMARY KEY,
    UserName VARCHAR,
    AverageStars DECIMAL,  
    YelpingSince DATETIME,
);

CREATE TABLE Review(
    UserID VARCHAR(25) FOREIGN KEY REFERENCES [User].[UserID],
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],    Review VARCHAR(1024) NOT NULL, 
    Funny INTEGER DEFAULT 0,
    Cool INTEGER DEFAULT 0,
    Useful INTEGER DEFAULT 0,
    PRIMARY KEY (UserID, BusinessID),
);


CREATE TABLE CheckIn(
    UserID VARCHAR(25) FOREIGN KEY REFERENCES [User].[userID],
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],
    CheckInDate DATETIME NOT NULL,
    PRIMARY KEY (UserID, BusinessID),
);

CREATE TABLE Business(
    BusinessID VARCHAR(25) PRIMARY KEY,
    BusinessName VARCHAR(80),
    Stars INTEGER,
    IsOpen BOOLEAN,
    PriceRange INTEGER NULL,
    AddressID INTEGER FOREIGN KEY REFERENCES [Address].[AddressID]
);

CREATE TABLE BusinessCategory(
    BusinessID VARCHAR(25) FOREIGN KEY REFERENCES [Business].[BusinessID],
    CategoryID INT FOREIGN KEY REFERENCES [Category].[CategoryID],
)

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