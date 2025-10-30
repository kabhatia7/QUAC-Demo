CREATE TABLE `quac_tech_demo`
(
  -- Columns from Roster data
  `Name` STRING,
  `userid` STRING,
  `Direct_Manager` STRING,
  `Pledge_Class` STRING,
  `Major` STRING,
  `Concentration` STRING,
  `Academic_Year` STRING,
  `Expected_Grad` STRING,
  
  -- Columns from Work data
  `Fundraising` FLOAT64,
  `Philanthropy` FLOAT64,
  `Professionalism` FLOAT64,
  `Brotherhood` FLOAT64,
  `week_end_date` DATE,
  `week_start_date` DATE
);