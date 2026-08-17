CS 499 Milestone Four Artifact Files
John Rosario

Enhancement Three: Databases

This technical artifact package uses the same base project as the prior enhancements:
the Grazioso Salvare Animal Shelter Dashboard.

Contents:
- Original_Project: Original Project Two dashboard artifact files.
- Enhanced_Project: Milestone Four database enhancement files.

Enhancement summary:
- Expanded the MongoDB access layer into a fuller CRUD interface with create, read, update, delete, count, and distinct methods.
- Added environment-driven connection settings and URI escaping for safer database configuration.
- Added query and projection validation to reduce unsafe or unsupported database requests.
- Added projection-limited reads so the dashboard retrieves only the fields it needs.
- Added query limit and sort support for more controlled database access.
- Added database index creation for common dashboard filter fields.
- Updated the dashboard to use the enhanced database interface and projection-limited queries.
