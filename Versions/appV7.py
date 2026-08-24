#### READ COMMENTS###


# previouly graph didn't auto update


import streamlit as st
from streamlit_folium import st_folium

# importing backend routing from other file
from Versions.mainV2 import EcoRoute


# page setup
st.set_page_config(page_title="EcoRoute",
                   page_icon="🌱", layout="wide")

VEHICLES = {"Select Vehicle": (None),
            "Hatchback (1300 kg)": (1300),
            "Sedan (1500 kg)": (1500),
            "SUV (1900 kg)": (1900),
            "Ute (2200 kg)": (2200),
            "I Know My Vehicle's Weight": (None),
            }

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


# loading graph from main.py
@st.cache_resource(show_spinner="Loading Wellington Road Network...")
def load_app():
    app = EcoRoute()
    app.load_or_build_graph()
    return app


app = load_app()

# page setup
st.title("EcoRoute")
st.caption("EcoRoute is a smart mapping application that uses graph theory, elevation information, and physics principles to determine the most fuel-efficient route between two points. EcoRoute stands out from traditional 2D navigation tools by considering elevation changes, friction and air resistance to select the route that minimises the vehicle’s energy consumption. This allows users to save fuel and reduce carbon emissions. Using mathematics, computer science and physics, EcoRoute offers smart navigation that benefits both drivers and the environment.")

# sidebar for input
with st.sidebar:
    st.header("Plan a route")

    vehicle = st.selectbox("Vehicle Weight", list(
        VEHICLES.keys()), index=0, placeholder="Choose option")

    # custom vehicle options
    if vehicle == "I Know My Vehicle's Weight":

        weight = st.number_input(
            "Weight (kg)", value=1500.0, format="%.1f", key="custom_vehicle_weight", step=50.0)
        # didnt have key = "custom vehicle weight"

    else:
        # Was error here""" vehicle was location
        weight = VEHICLES[vehicle]
        # Was error here"""

    if weight is not None:

        app.get_ALPHA(weight)
        # (app, "update eco costs")
        # update graph - this wasn't in v1"""
        app.update_eco_costs()
        # update graph - this wasn't in v1"""

        # select box for options
        start_name = st.selectbox("Start", list(LOCATIONS.keys()), index=0)
        end_name = st.selectbox("End", list(LOCATIONS.keys()), index=1)

        # custom coordinates options
        if start_name == "Custom Coordinates":

            start_lat = st.number_input("Start Latitude", format="%.5f")
            start_long = st.number_input("Start Longitude", format="%.5f")
            start_coords = (start_lat, start_long)
        else:
            start_coords = LOCATIONS[start_name]

        if end_name == "Custom Coordinates":

            end_lat = st.number_input("End Latitude", format="%.5f")
            end_long = st.number_input("End Longitude", format="%.5f")
            end_coords = (end_lat, end_long)
        else:
            end_coords = LOCATIONS[end_name]

        find_route = st.button("Find Route", type="primary",
                               use_container_width=True)

    else:
        find_route = False
        st.error("Please select a vehicle type")

if find_route:
    # display error
    if start_name == end_name and start_name != "Custom Coordinates":
        st.sidebar.error("Pick two different locations")
    else:
        # plot route
        with st.spinner("Loading routes"):
            m, standard_distance, eco_distance, standard_eco_cost, eco_eco_cost = app.plot_route(
                start_coords, end_coords)

            # save route
            st.session_state.m = m
            st.session_state.standard_distance = standard_distance
            st.session_state.eco_distance = eco_distance
            st.session_state.standard_eco_cost = standard_eco_cost
            st.session_state.eco_eco_cost = eco_eco_cost
            st.session_state.has_route = True

if st.session_state.get("has_route", False):

    # display route
    st_data = st_folium(st.session_state.m, width=1200,
                        height=600, returned_objects=[])

    std_cost = st.session_state.standard_eco_cost
    eco_cost = st.session_state.eco_eco_cost

    if std_cost > 0:
        savings_pct = ((std_cost - eco_cost) / std_cost) * 100
    else:
        savings_pct = 0.0

    if savings_pct > 0:
        d_arrow = "down"
    elif savings_pct < 0:
        d_arrow = "up"

    # display data
    col1, col2, col3 = st.columns(3)
    col1.metric("Standard Distance",
                f"{st.session_state.standard_distance:.0f} m")
    col2.metric("Eco Route Distance",
                f"{st.session_state.eco_distance:.0f} m")
    col3.metric("Energy Savings", f"{savings_pct:.1f}%",
                delta=f"{savings_pct:.1f}% lower energy cost", delta_color="normal", delta_arrow=d_arrow)

    # extra info
    with st.expander("How does this work?"):
        st.markdown(
            "Each road segments 'eco_cost' combines its physical length with a penalty for uphills:"
            "\n\nEco_cost = Distance x (1 + ALPHA x Grade) - Where ALPHA is 48.49.Refer to the logbook to see where 48.49 came from "
            "\n\n The **Standard Route** (red) minimises distance, while the **Eco Route** (green) minimises the eco-cost "
            "- both of which are found using Dijkstras algorithm on the same road network.")
