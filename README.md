Delivery Route Finder (BFS + MySQL)
A Python script that finds the shortest path for a delivery across a city grid stored in MySQL, using an 8-directional Breadth-First Search (BFS), and logs the results back to the database.
Overview
The script:
Connects to a MySQL database and lists available city maps (`map_id`s).
Loads the chosen map as a 2D grid (`0` = walkable, non-zero = obstacle) from the `city_map` table.
Prompts for a start point, end point, and a cost-per-unit-distance value.
Runs a BFS search (allowing diagonal moves, with diagonal steps weighted `√2`) to find the shortest path.
Computes total distance and total delivery cost.
Saves the result to `delivery_results`, and additionally to `delivery_success` or `delivery_failed` depending on outcome.
Requirements
Python 3.8+
MySQL server with a database containing a `city_map` table
Python packages:
```bash
  pip install mysql-connector-python numpy
  ```
Database Schema
Input table (must already exist)
```sql
CREATE TABLE city_map (
    map_id     INT,
    row_index  INT,
    col_index  INT,
    cell_value INT   -- 0 = walkable, non-zero = blocked
);
```
Output tables (auto-created by the script)
delivery_results — every run (success or failure), with `algorithm_used` and `status` columns.
delivery_success — only successful runs.
delivery_failed — only failed runs (no path found).
Usage
Run the script:
```bash
python delivery_route_finder.py
```
You will be prompted for:
Prompt	Description
Database password	MySQL password
Database name	Name of the MySQL database to connect to
Map ID to run	One of the available `map_id`s shown
Start X / Start Y	Starting grid coordinates
End X / End Y	Destination grid coordinates
Cost per unit distance	Multiplier used to compute total delivery cost
Example Session
```
Available Map IDs: [1, 2, 3]
Enter Map ID to run: 1

Map ID 1 Grid:
[0, 0, 1, 0]
[0, 1, 0, 0]
[0, 0, 0, 0]

Enter custom start and end coordinates for this map:
Start X: 0
Start Y: 0
End X: 2
End Y: 3
Enter cost per unit distance: 2.5

Shortest Distance: 4.243
Total Cost: 10.607
Path: [(0, 0), (1, 0), (2, 1), (2, 2), (2, 3)]

Path and cost saved successfully to database.
```
Algorithm Notes
Movement is allowed in 8 directions (up, down, left, right, and 4 diagonals).
Orthogonal moves cost `1`; diagonal moves cost `√2 ≈ 1.414`.
If no path exists between start and end, the script reports `"Delivery not possible"` and logs a `Failed` status with `NULL` distance/cost.
Known Limitations / Possible Improvements
BFS finds the shortest path in terms of steps, but since costs are weighted (√2 for diagonals), a true shortest-weighted-path would need Dijkstra's algorithm instead of BFS for guaranteed optimality.
No input validation on coordinates (e.g., out-of-bounds or landing on an obstacle isn't explicitly checked before search).
Database credentials are entered interactively each run; consider using environment variables or a config file for repeated use.
No indexes specified on `city_map(map_id)`, which could slow down lookups on large datasets.
