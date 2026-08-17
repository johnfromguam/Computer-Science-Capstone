CS 499 Milestone Three Artifact Files
John Rosario

Enhancement Two: Algorithms and Data Structures

This technical artifact package uses the same base project as the prior enhancement:
the Grazioso Salvare Animal Shelter Dashboard.

Contents:
- Original_Project: Original Project Two dashboard artifact files.
- Enhanced_Project: Milestone Three algorithms and data structures enhancement files.

Enhancement summary:
- Replaced repeated conditional rescue-filter logic with the RESCUE_PROFILES dictionary.
- Used frozensets for breed groups and tuples for age ranges so rescue criteria are centralized and reusable.
- Rebuilt the MongoDB query construction algorithm around those data structures.
- Added a Counter-based breed aggregation helper for the chart.
- Added helper algorithms for data normalization, selected-row validation, and safe coordinate conversion.
- Removed duplicated query logic and corrected fragile filtering/map behavior from the original dashboard.
