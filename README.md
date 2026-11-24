<<<<<<< HEAD
# **ServiceNow Auto Assign Analytics**



Python automation pipeline for assigning tickets automatically, collecting ServiceNow ticket data and storing it in SQLite for analytics and Power BI reporting



##### **Features**



* Read tickets from ServiceNow, assign it to myself based on "In progress", "New" state. Skips if is already assigned 
* Extract ticket information
* Capture state, location and assignment data
* Store results in SQLite
* Support Incident and Catalog Task records
* Feed Power BI dashboards



##### **Tech Stack**



Python 3.14

Python Packages

selenium==4.53.0

Visual studio code

SQLite

ODBC drivers

Power BI

ServiceNow web URL



##### **Architecture**



ServiceNow ↓ Python Selenium ↓ SQLite ↓ Power BI



##### **Data Collected**



Ticket Number

State

Location

Assignment Group

Timestamp



##### **Future Enhancements**



SLA Collection

Category Analytics

Priority Analytics

Power BI Dashboard

dbt Models





=======
# servicenow-auto-assign-ticket-analytics
ServiceNow ticket auto assign, Ticket collection, SQLite storage and Power BI reporting solution.
>>>>>>> c566dc58000524af427da4c9546dc794e9abe42b
