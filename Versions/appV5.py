import streamlit as st
from streamlit_folium import st_folium

# importing backend routing from other file
from Versions.main import EcoRoute

# page setup
st.set_page_config(page_title="EcoRoute",
                   page_icon="🌱", layout="wide")


# Preset Locations for demonstration
LOCATIONS = {"Grenada Village": (-41.2100737, 174.8237328),
             "Bowen Street, Thorndon": (-41.2788152, 174.7769341),
             "Wellington Railway Station": (-41.2793, 174.7803),
             "Te Papa": (-41.2903, 174.7818),
             "Karori": (-41.2833, 174.7333),
             "Newtown": (-41.3122, 174.7794),
             "Khandallah": (-41.2461, 174.7897),
             "Miramar": (-41.3167, 174.8167),
             "Custom Coordinates": (None)}


# loading the map from other file
@st.cache_resource(show_spinner="Loading Wellington Road Network...")
def load_app():
    app = EcoRoute()  # the imported class
    app.load_or_build_graph()
    return app


app = load_app()

# title
st.title("EcoRoute")
st.caption("EcoRoute is a smart mapping application that uses graph theory, elevation information, and physics principles to determine the most fuel-efficient route between two points. EcoRoute stands out from traditional 2D navigation tools by considering elevation changes, friction and air resistance to select the route that minimises the vehicle’s energy consumption. This allows users to save fuel and reduce carbon emissions. Using mathematics, computer science and physics, EcoRoute offers smart navigation that benefits both drivers and the environment.")

# sidebar for route planing
with st.sidebar:
    st.header("Plan a route")

    # provides options from dictionaries
    start_name = st.selectbox("Start", list(LOCATIONS.keys()), index=0)
    end_name = st.selectbox("End", list(LOCATIONS.keys()), index=1)

    if start_name == "Custom Coordinates":

        start_lat = st.number_input("Start Latitude", format="%.5f")
        start_long = st.number_input("Start Longitude", format="%.5f")
        start_coords = (start_lat, start_long)

    elif end_name == "Custom Coordinates":

        end_lat = st.number_input("End Latitude", format="%.5f")
        end_long = st.number_input("End Longitude", format="%.5f")
        end_coords = (end_lat, end_long)
    else:
        end_coords = LOCATIONS[end_name]
        start_coords = LOCATIONS[start_name]

    find_route = st.button("Find Route", type="primary",
                           use_container_width=True)

if find_route:
    if start_name == end_name:
        st.sidebar.error("Pick two different locations")
    else:
        with st.spinner("Loading routes"):
            m = app.plot_route(
                start_coords, end_coords)
            #
    st_data = st_folium(m, width=1200,
                        height=600)
