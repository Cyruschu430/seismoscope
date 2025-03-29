import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(page_title="SeismoScope", layout="wide")

# Load data from USGS API
@st.cache_data(ttl=300)
def load_data():
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        records = [
            {
                "place": feature["properties"]["place"],
                "mag": feature["properties"]["mag"],
                "time": pd.to_datetime(feature["properties"]["time"], unit="ms"),
                "longitude": feature["geometry"]["coordinates"][0],
                "latitude": feature["geometry"]["coordinates"][1],
                "depth": feature["geometry"]["coordinates"][2],
            }
            for feature in data["features"]
        ]
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error loading earthquake data: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("🌍 SeismoScope: Real-Time Global Earthquake Dashboard")

    df = load_data()

    if not df.empty:
        st.sidebar.header("🔍 Filters")
        min_datetime = df["time"].min()
        max_datetime = df["time"].max()
        default_start = max_datetime - timedelta(hours=24)

        start_date = st.sidebar.date_input("Start Date (UTC)", default_start.date(), min_value=min_datetime.date(), max_value=max_datetime.date())
        start_time = st.sidebar.time_input("Start Time (UTC)", default_start.time())
        end_date = st.sidebar.date_input("End Date (UTC)", max_datetime.date(), min_value=start_date, max_value=max_datetime.date())
        end_time = st.sidebar.time_input("End Time (UTC)", max_datetime.time())

        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)

        min_mag = st.sidebar.slider("Minimum Magnitude", 0.0, 10.0, 2.5, step=0.1)
        max_mag = st.sidebar.slider("Maximum Magnitude", min_mag, 10.0, 10.0, step=0.1)

        show_heatmap = st.sidebar.checkbox("🔥 Show Heatmap Layer")

        st.sidebar.markdown("---")
        auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=False)
        refresh_interval = st.sidebar.slider("Refresh Interval (minutes)", 1, 30, 5) if auto_refresh else None

        filtered_df = df[
            (df["mag"] >= min_mag) &
            (df["mag"] <= max_mag) &
            (df["time"] >= pd.to_datetime(start_datetime)) &
            (df["time"] <= pd.to_datetime(end_datetime))
        ].copy()

        tab1, tab2, tab3, tab4 = st.tabs(["🗺 Map", "📊 Table", "📈 Analysis", "📚 Learn"])

        with tab1:
            st.subheader("🗺 Earthquake Map")
            st.markdown("> **Map Description:** This interactive map displays global earthquakes. Each circle represents an earthquake. The size is scaled by magnitude. Use the filters on the sidebar to refine the results.")

            scatter_layer = pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position=["longitude", "latitude"],
                get_radius="mag * 50000",
                get_color=[255, 140, 0, 160],
                pickable=True,
                auto_highlight=True,
            )

            layers = [scatter_layer]

            if show_heatmap:
                heatmap_layer = pdk.Layer(
                    "HeatmapLayer",
                    data=filtered_df,
                    get_position="[longitude, latitude]",
                    aggregation='MEAN',
                    get_weight="mag",
                    opacity=0.6,
                )
                layers.append(heatmap_layer)

            view_state = pdk.ViewState(latitude=0, longitude=150, zoom=2, pitch=40)

            st.pydeck_chart(pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip={"text": "Location: {place}\nMagnitude: {mag}"},
                map_provider="mapbox",
                map_style="mapbox://styles/mapbox/dark-v10"
            ))
            st.markdown(f"Showing **{len(filtered_df)}** earthquakes with magnitude between **{min_mag}** and **{max_mag}**")

        with tab2:
            st.subheader("📊 Earthquake Data")
            sort_option = st.radio("Sort by:", options=["Latest First", "Oldest First"], horizontal=True, index=0)
            display_df = filtered_df.sort_values(by="time", ascending=(sort_option == "Oldest First"))
            st.dataframe(display_df[["time", "place", "mag", "depth", "latitude", "longitude"]], use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("⬇️ Download CSV", display_df.to_csv(index=False), file_name="earthquakes.csv", mime="text/csv")
            with col2:
                buffer = BytesIO()
                display_df.to_excel(buffer, index=False)
                st.download_button("⬇️ Download Excel", buffer.getvalue(), file_name="earthquakes.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        with tab3:
            st.subheader("📈 Spatial & Statistical Analysis")
            col1, col2 = st.columns(2)

            with col1:
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                sns.histplot(filtered_df["mag"], bins=15, kde=True, color="orange", ax=ax1)
                ax1.set_title("Magnitude Distribution")
                ax1.set_xlabel("Magnitude")
                ax1.set_ylabel("Frequency")
                st.pyplot(fig1)

            with col2:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                sns.regplot(data=filtered_df, x="mag", y="depth", scatter_kws={'alpha': 0.5}, line_kws={"color": "red"}, ax=ax2)
                ax2.set_title("Magnitude vs. Depth")
                ax2.set_xlabel("Magnitude")
                ax2.set_ylabel("Depth (km)")
                st.pyplot(fig2)

        with tab4:
            with st.expander("🧠 Learn More: What is an Earthquake?"):
                st.markdown("### 🌍 What Is an Earthquake?")
                st.markdown("""
                An earthquake is the shaking of the Earth's surface caused by a sudden release of energy in the planet’s crust.
                This energy radiates in all directions as seismic waves, which you feel as the ground shaking.
                """)
                st.image("assets/plate_tectonics.gif", caption="Tectonic plate movement", width=400)

                st.markdown("---")
                st.markdown("### 🧭 Why Do Earthquakes Happen?")
                col_eq1, col_eq2 = st.columns([2, 1])
                with col_eq1:
                    st.markdown("""
                    Earthquakes mainly occur due to the movement of tectonic plates, which are giant slabs of Earth's lithosphere:
                    - Collide *(convergent boundaries)*
                    - Slide past each other *(transform boundaries)*
                    - Pull apart *(divergent boundaries)*

                    When pressure builds up at these boundaries and exceeds the strength of rocks,
                    it gets released suddenly — causing an earthquake.
                    """)
                with col_eq2:
                    st.image("assets/earthquake.png", caption="How earthquakes happen", use_container_width=True)

                st.markdown("---")
                st.markdown("### 🌋 Where Are Earthquakes Most Common?")
                col_ring1, col_ring2 = st.columns([1.5, 2])
                with col_ring1:
                    st.image("assets/pacific-ring-of-fire.png", caption="Pacific Ring of Fire", use_container_width=True)
                with col_ring2:
                    st.markdown("""
                    The **Pacific Ring of Fire** is the most earthquake-prone region on Earth.
                    It’s a horseshoe-shaped zone around the Pacific Ocean where several tectonic plates meet and shift.

                    > 💡 *Fun Fact: Over 80% of the world’s largest earthquakes occur in this region!*
                    """)

                st.markdown("---")
                st.markdown("### 🛟 Earthquake Safety Tips")
                col_safety1, col_safety2 = st.columns([2, 1])
                with col_safety1:
                    st.markdown("""
                    **✅ Before an Earthquake**
                    - Secure heavy furniture and shelves.
                    - Know safe spots (under sturdy furniture, away from windows).

                    **⚠️ During an Earthquake**
                    - Drop to your hands and knees.
                    - Cover your head and neck under a table or desk.
                    - Hold On until the shaking stops.

                    **🌊 If You're Near the Coast**
                    - Move to higher ground immediately if you feel strong shaking — it could trigger a tsunami.

                    **🧳 Emergency Kit Checklist**
                    - Water, food, flashlight, radio, batteries, first aid supplies.
                    """)
                with col_safety2:
                    st.image("assets/safety_tips.png", caption="Earthquake safety checklist", use_container_width=True)

            with st.expander("🧪 Earthquake Quick Quiz"):
                st.markdown("Test your earthquake knowledge!")

                q1 = st.radio("1️⃣ What causes most earthquakes?", [
                    "Weather patterns",
                    "Tectonic plate movements",
                    "Human activity",
                    "Moon gravity"
                ])
                if q1 == "Tectonic plate movements":
                    st.success("✅ Correct!")
                elif q1 != "":
                    st.error("❌ Oops! The correct answer is: Tectonic plate movements.")

                q2 = st.selectbox("2️⃣ Where is the 'Ring of Fire' located?", [
                    "Atlantic Ocean", "Indian Ocean", "Pacific Ocean", "Arctic Ocean"
                ])
                if q2 == "Pacific Ocean":
                    st.success("✅ You're right!")
                elif q2 != "":
                    st.error("❌ It's the Pacific Ocean.")

                st.markdown("3️⃣ True or False: You should run outside during an earthquake.")
                col1, col2 = st.columns(2)
                with col1:
                    tf_true = st.checkbox("True", key="q3_true")
                with col2:
                    tf_false = st.checkbox("False", key="q3_false")

                if tf_true and not tf_false:
                    st.error("❌ It's safer to stay inside and drop, cover, and hold on.")
                elif tf_false and not tf_true:
                    st.success("✅ Correct! Stay inside and protect yourself.")
                elif tf_true and tf_false:
                    st.warning("⚠️ Please select only one option.")

        # Footer and refresh logic
        st.markdown("""
        <hr>
        <footer style='text-align: center; color: gray;'>
            Built with ❤️ by Cyrus Chu | Updated every 30 minutes | Powered by USGS API
        </footer>
        """, unsafe_allow_html=True)

        if auto_refresh:
            st.sidebar.success(f"App will refresh every {refresh_interval} minute(s)...")
            time.sleep(refresh_interval * 60)
            st.experimental_rerun()

    else:
        st.error("Unable to load earthquake data. Please try again later.")

if __name__ == "__main__":
    main()
