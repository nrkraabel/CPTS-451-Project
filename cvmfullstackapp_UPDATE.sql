
DROP TABLE IF EXISTS BusinessAggregates;

CREATE TEMP TABLE BusinessAggregates AS
SELECT
    b.BusinessID,
    COALESCE(SUM(c.COUNT), 0) AS numCheckins,
    COUNT(r.ReviewID) AS reviewcount,
    COALESCE(AVG(r.ReviewStars), 0) AS reviewrating
FROM
    Business b
LEFT JOIN CheckIn c ON b.BusinessID = c.BusinessID
LEFT JOIN Review r ON b.BusinessID = r.BusinessID
GROUP BY
    b.BusinessID;

UPDATE Business
SET
    CheckIns = ba.numCheckins,
    ReviewCount = ba.reviewcount,
    ReviewRating = ba.reviewrating
FROM
    BusinessAggregates ba
WHERE
    Business.BusinessID = ba.BusinessID;
