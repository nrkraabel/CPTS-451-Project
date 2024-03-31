--Popular Businesses
WITH CategoryAverageCheckIns AS (
    SELECT
        bc.CategoryID,
        AVG(c.COUNT) AS AvgCheckIns
    FROM
        CheckIn c
    JOIN BusinessCategory bc ON c.BusinessID = bc.BusinessID
    GROUP BY bc.CategoryID
),
BusinessCheckIns AS (
    SELECT
        c.BusinessID,
        SUM(c.COUNT) AS TotalCheckIns
    FROM CheckIn c
    GROUP BY c.BusinessID
),
CategoryAverageReviews AS (
    SELECT
        bc.CategoryID,
        AVG(sub.ReviewCount) AS AvgReviewCount
    FROM
        BusinessCategory bc
    JOIN (
        SELECT
            r.BusinessID,
            COUNT(*) AS ReviewCount
        FROM Review r
        GROUP BY r.BusinessID
    ) sub ON bc.BusinessID = sub.BusinessID
    GROUP BY bc.CategoryID
),
BusinessReviews AS (
    SELECT
        r.BusinessID,
        COUNT(*) AS TotalReviews
    FROM Review r
    GROUP BY r.BusinessID
)
SELECT
    DISTINCT b.BusinessID,
    b.BusinessName,
    bci.TotalCheckIns,
    br.TotalReviews
FROM
    Business b
JOIN BusinessCheckIns bci ON b.BusinessID = bci.BusinessID
JOIN BusinessReviews br ON b.BusinessID = br.BusinessID
JOIN BusinessCategory bc ON b.BusinessID = bc.BusinessID
JOIN CategoryAverageCheckIns caci ON bc.CategoryID = caci.CategoryID
JOIN CategoryAverageReviews car ON bc.CategoryID = car.CategoryID
WHERE
    bci.TotalCheckIns > caci.AvgCheckIns AND
    br.TotalReviews > car.AvgReviewCount
ORDER BY
    b.BusinessName;




--Succesful Businesses
WITH BusinessAge AS (
    SELECT
        b.BusinessID,
        MIN(r.ReviewDate) AS FirstReviewDate,
        EXTRACT(YEAR FROM AGE(TIMESTAMP '2023-04-01', MIN(r.ReviewDate))) AS YearsInOperation
    FROM
        Business b
    JOIN
        Review r ON b.BusinessID = r.BusinessID
    GROUP BY
        b.BusinessID
    HAVING
        EXTRACT(YEAR FROM AGE(TIMESTAMP '2023-04-01', MIN(r.ReviewDate))) >= 3
),
CategoryAverageCheckIns AS (
    SELECT
        bc.CategoryID,
        AVG(c.COUNT) AS AvgCheckIns
    FROM
        CheckIn c
    JOIN
        BusinessCategory bc ON c.BusinessID = bc.BusinessID
    GROUP BY
        bc.CategoryID
),
BusinessCheckIns AS (
    SELECT
        c.BusinessID,
        SUM(c.COUNT) AS TotalCheckIns
    FROM
        CheckIn c
    GROUP BY
        c.BusinessID
),
FilteredBusinesses AS (
    SELECT DISTINCT
        b.BusinessID,
        b.BusinessName,
        b.Stars,
        ba.YearsInOperation,
        bci.TotalCheckIns
    FROM
        Business b
    JOIN
        BusinessAge ba ON b.BusinessID = ba.BusinessID
    JOIN
        BusinessCheckIns bci ON b.BusinessID = bci.BusinessID
)
SELECT
    fb.BusinessID,
    fb.BusinessName,
    fb.Stars,
    fb.YearsInOperation,
    fb.TotalCheckIns
FROM
    FilteredBusinesses fb
JOIN
    BusinessCategory bc ON fb.BusinessID = bc.BusinessID
JOIN
    CategoryAverageCheckIns cai ON bc.CategoryID = cai.CategoryID
WHERE
    fb.TotalCheckIns > cai.AvgCheckIns
    AND fb.Stars > 4
GROUP BY
    fb.BusinessID, fb.BusinessName, fb.Stars, fb.YearsInOperation, fb.TotalCheckIns
HAVING
    COUNT(DISTINCT bc.CategoryID) >= 1; 


--Expensive
SELECT DISTINCT
    b.BusinessID,
    b.BusinessName
FROM
    Business b
JOIN
    Review r ON b.BusinessID = r.BusinessID
WHERE
    LOWER(r.ReviewText) LIKE '%high priced%' OR
    LOWER(r.ReviewText) LIKE '%high cost%' OR
    LOWER(r.ReviewText) LIKE '%expensive%' OR
    LOWER(r.ReviewText) LIKE '%that’s a bit pricey%' OR
    LOWER(r.ReviewText) LIKE '%costs an arm and a leg%' OR
    LOWER(r.ReviewText) LIKE '%exorbitant%' OR
    LOWER(r.ReviewText) LIKE '%costly%' OR
    LOWER(r.ReviewText) LIKE '%high end%' OR
    LOWER(r.ReviewText) LIKE '%pricey%'
ORDER BY
    b.BusinessName;