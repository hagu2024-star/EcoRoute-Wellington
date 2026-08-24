import folium as fl
import osmnx as ox

# Global default coordinates for Wellington
COORDINATES = (-41.28664, 174.77557)


class EcoRoute:

    def __init__(self):
        # Naming location
        self.location_name = "Wellington, New Zealand"
        self.COORDINATES = COORDINATES
        self.ALPHA = 48.49  # Physics constant derived from Work = Force * Distance

    def build_graph(self):
        # Building the graph
        print("Downloading map data...")
        self.graph = ox.graph_from_place(
            self.location_name, network_type="drive"
        )

        # Configure Open Topo Data API
        ox.settings.elevation_url_template = (
            "https://api.opentopodata.org/v1/aster30m?locations={locations}"
        )

        print("Fetching elevation data...")
        # Downloading data from Open Topo Data API
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
        # ___This section calculates, and saves all the edge costs___ #

        # Creating visual map around Wellington
        m = fl.Map(
            location=self.COORDINATES,  # location
            zoom_start=13,  # how zoomed in at start
            zoom_control=True,  # zoom buttons
            control_scale=True,  # distance scale
        )

        # Saving base map to html file
        m.save("map.html")
        print("Success! 'map.html' generated with eco_cost graph.")


# Running the class.
if __name__ == "__main__":
    app = EcoRoute()
    app.build_graph()
