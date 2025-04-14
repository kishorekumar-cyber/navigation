from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import heapq

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the enhanced graph with coordinates
with open("navigation_graph_with_cricket_ground.json", "r") as f:
    graph = json.load(f)

# Aliases for flexible input
place_aliases = {
    "girls hostel": "girl's hostel",
    "the girls hostel": "girl's hostel",
    "hostel for girls": "girl's hostel",
    "boys hostel": "boy's hostel",
    "the boys hostel": "boy's hostel",
    "main block": "engineering main block",
    "rear block": "engineering rear block",
    "mech lab": "mechanical and electrical lab",
    "polytechnic and first year's block": "polytechnic and engg 1st year's block",
    "polytechnic and first year block": "polytechnic and engg 1st year's block",
    "polytech college": "polytechnic and engg 1st year's block",
    "first year block": "polytechnic and engg 1st year's block",
    "polytechnic and engineering first year's block": "polytechnic and engg 1st year's block",
    "ias cell": "placement and IAS academy",
    "placement cell": "placement and IAS academy",
    "turf": "cricket turf",
    "arts and science college": "arts and science block",
    "main gate": "Main gate",
    "cricket ground": "Cricket ground",
    "criket ground": "Cricket ground"
}

# Normalize user input
def normalize_place(name):
    name = name.lower().strip()
    return place_aliases.get(name, name)

# Match normalized name to graph node
def match_place(input_name):
    norm = normalize_place(input_name)
    norm = norm.lower()
    for place in graph:
        if place.lower() == norm:
            return place  # Return the real key (with correct casing)
    return None

# Dijkstra's algorithm on enhanced graph
def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == end:
            return (path, cost)

        neighbors = graph[node].get("connections", {})
        for neighbor, weight in neighbors.items():
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return (None, float("inf"))

# Main logic function
def get_directions(source_input, destination_input):
    source = match_place(source_input)
    destination = match_place(destination_input)

    if not source or not destination:
        return "❌ One or both locations were not found in the campus map."

    source_conn = graph[source].get("connections", {})
    dest_conn = graph[destination].get("connections", {})

    warning = ""
    if len(source_conn) < 2:
        warning += f"⚠️ '{source}' has very few direct paths. Routing may be indirect.\n"
    if len(dest_conn) < 2:
        warning += f"⚠️ '{destination}' has very few direct paths. Routing may be indirect.\n"

    path, total_distance = dijkstra(graph, source, destination)
    if path:
        steps = " → ".join(path)
        return warning + f"📍 Route: {steps}\n🧭 Total distance: {int(total_distance)} meters"
    else:
        return warning + "⚠️ No path found between those locations."

# Flask route
@app.route("/get-directions", methods=["POST"])
def get_directions_api():
    data = request.get_json()
    source = data.get("source")
    destination = data.get("destination")

    if not source or not destination:
        return jsonify({"error": "Missing source or destination"}), 400

    result = get_directions(source, destination)
    return jsonify({"result": result})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
