import streamlit as st
from streamlit_folium import st_folium

import matplotlib.pyplot as plt

# importing backend routing from other file
from main import EcoRoute


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
LOCATIONS = {"Wellington Railway Station": (-41.2793, 174.7803),
             "Victoria University Kelburn": (-41.289952686820364, 174.76792996509707),
             "Grenada Village": (-41.2100737, 174.8237328),
             "Bowen Street, Thorndon": (-41.2788152, 174.7769341),
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

# tab setup
tab1, tab2, tab3, = st.tabs(
    ["Navigation", "Route Comparison", "How it Works"], width="stretch", height="content", default="Navigation")


with tab1:
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
            weight = VEHICLES[vehicle]

        if weight is not None:

            app.get_ALPHA(weight)
            # (app, "update eco costs")
            app.update_eco_costs()

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
                m, standard_distance, eco_distance, standard_eco_cost, eco_eco_cost, std_profile, eco_profile = app.plot_route(
                    start_coords, end_coords)

                # save route
                st.session_state.m = m
                st.session_state.standard_distance = standard_distance
                st.session_state.eco_distance = eco_distance
                st.session_state.standard_eco_cost = standard_eco_cost
                st.session_state.eco_eco_cost = eco_eco_cost
                st.session_state.std_profile = std_profile
                st.session_state.eco_profile = eco_profile
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

        with st.container(border=True):
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
            alpha_val = getattr(app, "ALPHA", None)
            if weight is not None and alpha_val is not None:
                st.markdown(
                    "Each road segment's 'eco_cost' combines its physical length with a penalty for uphills:\n\n"
                    f"$$\\text{{Eco\\_cost}} = \\text{{Distance}} \\times (1 + \\alpha \\times \\text{{Grade}})$$\n\n"
                    f"Where **$\\alpha$ = {alpha_val:.2f}** for your selected vehicle weight ({weight:.0f} kg).\n\n"
                    "The **Standard Route** (red) minimises distance while the **Eco Route** (green) minimises energy, "
                    "both of which are found using Dijkstra's algorithm on the same road network."
                )
            else:
                st.info(
                    "Select a vehicle in the sidebar to view dynamic parameters."
                )

with tab2:
    st.title("Route Comparison")

    if st.session_state.get("has_route", False):

        st.subheader("Route Data Comparison")
        standard_dist = st.session_state.standard_distance
        eco_dist = st.session_state.eco_distance
        std_cost = st.session_state.standard_eco_cost
        eco_cost = st.session_state.eco_eco_cost

        dist_diff = eco_dist - standard_dist

        if standard_dist > 0:
            dist_diff_pct = (dist_diff/standard_dist) * 100
        else:
            dist_diff_pct = 0

        cost_dif = std_cost - eco_cost
        if std_cost > 0:
            energy_saved_pct = (cost_dif/std_cost) * 100
        else:
            energy_saved_pct = 0

        fuel_saved_ml = max(0, cost_dif * 0.08)
        co2_saved_g = fuel_saved_ml * 2.31

        comparison_data = {
            "Metric": ["Path Distance", "Energy Cost Score", "Estimated Fuel", "Estimated CO₂"],
            "Standard Route (Red)": [f"{standard_dist:.0f} m", f"{std_cost:.1f}", f"{(standard_dist/1000)*0.08:.2f} L", f"{((standard_dist/1000)*0.08)*2310:.0f} g"],
            "EcoRoute (Green)": [f"{eco_dist:.0f} m", f"{eco_cost:.1f}", f"{((standard_dist/1000)*0.08) - (fuel_saved_ml/1000):.2f} L", f"{(((standard_dist/1000)*0.08)*2310) - co2_saved_g:.0f} g"],
            "Net Difference": [f"+{dist_diff:.0f} m ({dist_diff_pct:+.1f}%)", f"-{energy_saved_pct:.1f}% Energy", f"-{fuel_saved_ml:.1f} mL", f"-{co2_saved_g:.1f} g"]
        }
        st.table(comparison_data)

        st.subheader("Elevation Profile")

        # Create Matplotlib Plot
        fig, ax = plt.subplots(figsize=(10, 4))

        std_dists, std_elevs = st.session_state.std_profile
        eco_dists, eco_elevs = st.session_state.eco_profile

        # Plot line curves
        ax.plot(
            std_dists,
            std_elevs,
            label="Standard Route (Red)",
            color="#FF4B4B",
            linewidth=2.5,
        )
        ax.plot(
            eco_dists,
            eco_elevs,
            label="Eco Route (Green)",
            color="#00C04D",
            linewidth=2.5,
            linestyle="--",
        )

        ax.set_xlabel("Distance Traveled (metres)", fontsize=11)
        ax.set_ylabel("Elevation (metres above sea level)", fontsize=11)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(frameon=True)

        # Display chart in Streamlit
        st.pyplot(fig)

        # Additional metrics & takeaways
        max_std_elev = max(std_elevs) if std_elevs else 0
        max_eco_elev = max(eco_elevs) if eco_elevs else 0

        st.caption(
            f"**Peak Elevation Comparison:** Standard Route reaches **{max_std_elev:.1f} m** | "
            f"Eco Route reaches **{max_eco_elev:.1f} m**")

        st.subheader("Key Takeaways")
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(
                f"**Distance Trade-off:**\n"
                f"The EcoRoute adds **{max(0, dist_diff):.0f} meters** of extra travel distance, but bypasses steep elevation changes."
            )
        with col_b:
            st.success(
                f"**Energy Efficiency:**\n"
                f"Despite the extra distance, the vehicle engine performs **{energy_saved_pct:.1f}% less overall work**."
            )

    else:
        st.info(
            "Please select a vehicle and calculate a route in sidebar to generate analysis data")

with tab3:
    st.header("How it Works")
    st.caption(
        "The mathematics, physics, and graph theory behind EcoRoute.")

    # 1. Physics Forces Breakdown
    st.subheader("Vehicle Physics & Forces")
    st.markdown(
        "EcoRoute models the total mechanical force required to move a vehicle along any road segment using three primary physical forces:"
    )

    alpha_val = getattr(app, "ALPHA", None)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Rolling Friction ($F_{\\text{friction}}$)**")
        st.caption("Resistance between tires and road.")
        st.latex(r"F_{\text{friction}} = \mu \cdot m \cdot g")
    with col2:
        st.markdown("**Aerodynamic Drag ($F_{\\text{drag}}$)**")
        st.caption("Air resistance acting on the vehicle.")
        st.latex(r"F_{\text{drag}} = \frac{1}{2} \rho v^2 C_d A")
    with col3:
        st.markdown("**Gravitational Resistance ($F_{\\text{gravity}}$)**")
        st.caption("Extra force required to overcome slopes.")
        st.latex(r"F_{\text{gravity}} = m \cdot g \cdot \text{grade}")

    st.divider()

    # 2. Alpha Factor Derivation
    st.subheader("Elevation Penalty Factor ($\\alpha$)")

    if alpha_val is not None:
        st.success(
            f"**Live Parameter:** Selected Vehicle Weight $\\rightarrow$ **$\\alpha = {alpha_val:.2f}$**")
    else:
        st.info(
            "Please select a vehicle in the sidebar to display live dynamic parameters.")

    st.markdown(
        "The constant **$\\alpha$** quantifies the extra distance your vehicle could travel on flat land compared to using the same amount of fuel on an incline. "
        "Since heavier vehicles require more work to climb hills, $\\alpha$ scales dynamically with vehicle mass."
    )

    st.markdown(
        "Each road edge in the graph network is assigned an **Eco Cost** with this formula:"
    )
    st.latex(
        r"\text{Eco Cost} = \text{Distance} \times \max\left(0.2, \, 1 + \alpha \cdot \text{Grade}\right)")

    st.info(
        "**Note:** The lower cap of $0.2$ accounts for engine idling and braking losses, preventing negative or zero edge weights."
    )

    st.divider()

    # 3. Graph Theory & Routing Engine
    st.subheader("Graph Theory & Dijkstra's Algorithm")

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("### OpenStreetMap Graph Model")
        st.markdown(
            "* **Nodes ($V$):** Intersections and road endpoints embedded with 3D coordinates ($x, y, z$).\n"
            '* **Edges ($E$):** Directed roads carrying physical distance ($m$), grade ($\\theta$), and "eco_cost".'
        )
    with g_col2:
        st.markdown("### Pathfinding Execution")
        st.markdown(
            "* **Standard Route:** Uses Dijkstra's algorithm where edge weight $w_e = \\text{distance}$.\n"
            "* **EcoRoute:** Uses Dijkstra's algorithm where edge weight $w_e = \\text{eco\\_cost}$.\n"
        )
