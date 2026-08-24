import os
import folium as fl
import osmnx as ox
import networkx as nx

# Global default coordinates for Wellington
COORDINATES = (-41.28664, 174.77557)
GRAPH_FILE = "wellington_ecomap.graphml"
MAP_FILE = "map.html"


class EcoRoute:

    def __init__(self):
        # Naming location
        self.location_name = "Wellington, New Zealand"
        self.COORDINATES = COORDINATES
        self.ALPHA = 48.49  # physics constant derived from Work = Force * Distance

    def load_or_build_graph(self):
        # checking if the graph already exists and loading it
        if os.path.exists(GRAPH_FILE):
            print(f"Loading cached graph from {GRAPH_FILE}")
            self.graph = ox.load_graphml(
                GRAPH_FILE, edge_dtypes={"eco_cost": float})
            print("Graph loaded successfully")
            return

        # building the graph from scratch
        print("Downloading map data...")
        self.graph = ox.graph_from_place(
            self.location_name, network_type="drive"
        )

        # configure Open Topo Data API
        ox.settings.elevation_url_template = (
            "https://api.opentopodata.org/v1/aster30m?locations={locations}"
        )

        print("Fetching elevation data...")
        # downloading data from Open Topo Data API
        self.graph = ox.elevation.add_node_elevations_google(
            self.graph, batch_size=100, pause=1
        )
        self.graph = ox.elevation.add_edge_grades(self.graph)

        # Converting the graph into GeoDataFrames (for inspection/plotting)
        self.nodes, self.edges = ox.graph_to_gdfs(self.graph)

        print("Calculating eco-costs for edges...")
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            # 1. Get physical length in metres
            distance = data["length"]

            # 2. Gets road incline, defaults it to 0.0 if missing
            grade = data.get("grade", 0.0)

            # 3. Applies the physics formula for edges. Self.ALPHA is 48.49
            eco_factor = 1.0 + (self.ALPHA * grade)

            # 4. Cap minimum to 0.2, this accounts for coasting/idling
            eco_factor = max(0.2, eco_factor)

            # 5. Inject eco_cost into edge data dictionary
            data["eco_cost"] = distance * eco_factor
        # ___this section calculates and saves the eco costs___ #

        print(f"Saving graph as {GRAPH_FILE}")
        ox.save_graphml(self.graph, filepath=GRAPH_FILE)
        print(f"Saved graph successfully as {GRAPH_FILE}")

    def plot_route(self, start_coords, end_coords):

        # get nodes from coordinates
        start_node = ox.distance.nearest_nodes(
            self.graph, X=start_coords[1], Y=start_coords[0])
        end_node = ox.distance.nearest_nodes(
            self.graph, X=end_coords[1], Y=end_coords[0])

        # find standard path based on distance
        standard_path = nx.shortest_path(
            self.graph, start_node, end_node, weight="length")
        # finds eco friendly path using "eco_cost" as weight from earlier
        eco_path = nx.shortest_path(
            self.graph, start_node, end_node, weight="eco_cost")
        # nx.shortest_path uses Dijskra's algorithm by default.

        # converting the nodes back into coordinates for folium
        standard_coords = []
        for n in standard_path:
            standard_coords.append((
                self.graph.nodes[n]["y"], self.graph.nodes[n]["x"]))
        eco_coords = []
        for n in eco_path:
            eco_coords.append((
                self.graph.nodes[n]["y"], self.graph.nodes[n]["x"]))
        # note: OSMnx uses (latitude, longitude)

        # initialising visual map around starting point
        m = fl.Map(
            location=start_coords,  # location
            zoom_start=13,  # how zoomed in at start
            zoom_control=True,  # zoom buttons
            control_scale=True,  # distance scale
            world_copy_jump=True  # copying the marker when user scrolls beyond edge
        )

        # draw standard route
        fl.PolyLine(locations=standard_coords, color="#ff0000",
                    weight=5, tooltip="Standard Route", smooth_factor=0).add_to(m)
        # draw eco route
        fl.PolyLine(locations=eco_coords, color="#00ff00",
                    weight=5, tooltip="Eco Route", smooth_factor=0).add_to(m)

        # add start and end markers
        fl.Marker(location=start_coords, popup=start_coords,
                  icon=fl.Icon(color="green", icon="play")).add_to(m)
        fl.Marker(location=end_coords, popup=end_coords,
                  icon=fl.Icon(color="red", icon="flag")).add_to(m)

        # finding the total distance/cost for comparision
        standard_distance = nx.path_weight(
            self.graph, standard_path, weight="length")
        eco_distance = nx.path_weight(self.graph, eco_path, weight="length")
        standard_eco_cost = nx.path_weight(
            self.graph, standard_path, weight="eco_cost")
        eco_eco_cost = nx.path_weight(self.graph, eco_path, weight="eco_cost")

        # saving
        m.save(MAP_FILE)
        print("Route successfully plotted!")
        return m, standard_distance, eco_distance, standard_eco_cost, eco_eco_cost
