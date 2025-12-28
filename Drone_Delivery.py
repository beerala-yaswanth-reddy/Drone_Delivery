import mysql.connector
import numpy as np
from collections import deque
from math import sqrt

DB_CFG = {
    "host": "localhost",
    "user": "root",
    "password": input("Enter the password"),
    "database": input("Enter name of the database"),
    "auth_plugin": "mysql_native_password"
}

def bfs_shortest_path_with_cost(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    queue = deque([(start, [start], 0)])
    directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    while queue:
        (x, y), path, dist = queue.popleft()
        if (x, y) == end:
            return round(dist, 3), path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0 and (nx, ny) not in visited:
                step_dist = sqrt(2) if abs(dx) + abs(dy) == 2 else 1
                queue.append(((nx, ny), path + [(nx, ny)], dist + step_dist))
    return "Delivery not possible", []

def save_result_to_db(map_id, start, end, distance, path, total_cost):
    conn = mysql.connector.connect(**DB_CFG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS delivery_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            map_id INT,
            start_x INT,
            start_y INT,
            end_x INT,
            end_y INT,
            shortest_path TEXT,
            distance FLOAT,
            total_cost FLOAT,
            algorithm_used VARCHAR(50),
            status VARCHAR(20)
        )
    """)
    if isinstance(distance, str):
        status = "Failed"
        distance_val = None
        cost_val = None
        shortest_path = str(path)
    else:
        status = "Success"
        distance_val = round(distance, 3)
        cost_val = round(total_cost, 3)
        shortest_path = str(path)
    algorithm_used = "BFS with Distance Cost"
    cursor.execute("""
        INSERT INTO delivery_results 
        (map_id, start_x, start_y, end_x, end_y, shortest_path, distance, total_cost, algorithm_used, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (map_id, start[0], start[1], end[0], end[1],
          shortest_path, distance_val, cost_val, algorithm_used, status))
    if status == "Success":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delivery_success (
                id INT AUTO_INCREMENT PRIMARY KEY,
                map_id INT,
                start_x INT,
                start_y INT,
                end_x INT,
                end_y INT,
                shortest_path TEXT,
                distance FLOAT,
                total_cost FLOAT,
                status VARCHAR(20)
            )
        """)
        cursor.execute("""
            INSERT INTO delivery_success 
            (map_id, start_x, start_y, end_x, end_y, shortest_path, distance, total_cost, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (map_id, start[0], start[1], end[0], end[1],
              shortest_path, distance_val, cost_val, status))
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delivery_failed (
                id INT AUTO_INCREMENT PRIMARY KEY,
                map_id INT,
                start_x INT,
                start_y INT,
                end_x INT,
                end_y INT,
                shortest_path TEXT,
                distance FLOAT,
                total_cost FLOAT,
                status VARCHAR(20)
            )
        """)
        cursor.execute("""
            INSERT INTO delivery_failed 
            (map_id, start_x, start_y, end_x, end_y, shortest_path, distance, total_cost, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (map_id, start[0], start[1], end[0], end[1],
              shortest_path, distance_val, cost_val, status))
    conn.commit()
    conn.close()
    print("Path and cost saved successfully to database.")

def fetch_map_data(map_id):
    conn = mysql.connector.connect(**DB_CFG)
    cursor = conn.cursor()
    cursor.execute("SELECT row_index, col_index, cell_value FROM city_map WHERE map_id = %s ORDER BY row_index, col_index", (map_id,))
    data = cursor.fetchall()
    conn.close()
    if not data:
        return None
    rows = max(r for r, i, j in data) + 1
    cols = max(c for i, c, j in data) + 1
    grid = np.ones((rows, cols), dtype=int)
    for r, c, v in data:
        grid[r][c] = v
    return grid.tolist()

def main():
    try:
        conn = mysql.connector.connect(**DB_CFG)
        print("Connected to MySQL successfully.\n")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT map_id FROM city_map ORDER BY map_id ASC")
        available_maps = [row[0] for row in cursor.fetchall()]
        conn.close()
        if not available_maps:
            print("No maps available in database.")
            return
        print("Available Map IDs:", available_maps)
        map_id = int(input("Enter Map ID to run: "))
        grid = fetch_map_data(map_id)
        if not grid:
            print(f"Error fetching data: No data found for map_id {map_id}")
            return
        print(f"\nMap ID {map_id} Grid:\n")
        for row in grid:
            print(row)
        print("\nEnter custom start and end coordinates for this map:")
        start_x = int(input("Start X: "))
        start_y = int(input("Start Y: "))
        end_x = int(input("End X: "))
        end_y = int(input("End Y: "))
        cost_per_unit = float(input("Enter cost per unit distance: "))
        distance, path = bfs_shortest_path_with_cost(grid, (start_x, start_y), (end_x, end_y))
        if isinstance(distance, str):
            print("\nShortest Distance: Delivery not possible")
            total_cost = None
        else:
            total_cost = round(distance * cost_per_unit, 3)
            print(f"\nShortest Distance: {distance}")
            print(f"Total Cost: {total_cost}")
        print(f"Path: {path}\n")
        save_result_to_db(map_id, (start_x, start_y), (end_x, end_y), distance, path, total_cost)
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()  #this is my main function