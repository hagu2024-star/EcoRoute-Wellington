import streamlit as st
from streamlit_folium import st_folium

# importing backend routing from other file
from Versions.main import EcoRoute

# page setup
st.set_page_config(page_title="EcoRoute Wellington",
                   page_icon="🌱", layout="wide")


# Preset Locations for demonstration
LOCATIONS = {"Grenada Village": (-41.2100737, 174.8237328),
             "Bowen Street, Thorndon": (-41.2788152, 174.7769341),
             "Wellington Railway Station": (-41.2793, 174.7803),
             "Te Papa": (-41.2903, 174.7818),
             "Karori": (-41.2833, 174.7333),
             "Newtown": (-41.3122, 174.7794),
             "Khandallah": (-41.2461, 174.7897),
             "Miramar": (-41.3167, 174.8167), }


# loading graph
@st.cache_resource(show_spinner="Loading Wellington Road Network...")
def load_app():
    app = EcoRoute()
    app.load_or_build_graph()
    return app


app = load_app()

# title
st.title("EcoRoute")
st.caption("EcoRoute is a smart mapping application that uses graph theory, elevation information, and physics principles to determine the most fuel-efficient route between two points. EcoRoute stands out from traditional 2D navigation tools by considering elevation changes, friction and air resistance to select the route that minimises the vehicle’s energy consumption. This allows users to save fuel and reduce carbon emissions. Using mathematics, computer science and physics, EcoRoute offers smart navigation that benefits both drivers and the environment.")

# sidebar for route planning
with st.sidebar:
    st.header("Plan a route")

    # provides options from presets dictionary
    start_name = st.selectbox("Start", list(LOCATIONS.keys()), index=0)
    end_name = st.selectbox("End", list(LOCATIONS.keys()), index=1)

    # button to find the route
    find_route = st.button("Find Route", type="primary",
                           use_container_width=True)

if find_route:
    if start_name == end_name:
        # error if start is same as end
        st.sidebar.error("Pick two different locations")
    else:
        # plots route using code from main.py file and shows spinner while loading.
        with st.spinner("Loading routes"):
            app.plot_route(LOCATIONS[start_name], LOCATIONS[end_name])
