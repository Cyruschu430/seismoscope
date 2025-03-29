# 🌍 SeismoScope: Real-Time Global Earthquake Dashboard

**SeismoScope** is an interactive educational dashboard that visualizes real-time global earthquake activity using live data from the USGS API. Built with Python and Streamlit, the app makes seismic data accessible, visual, and engaging — with features designed for both exploration and learning.

🔗 **Live App:** [seismoscope.streamlit.app](https://seismoscope.streamlit.app)

---

## 🚀 Features

### 🌐 Earthquake Map
- Visualize earthquakes from the past 30 days
- Scaled markers by magnitude
- Optional heatmap layer for seismic density

### 📊 Interactive Filters
- Filter by date/time and magnitude range
- Auto-refresh every 5–30 minutes (optional)

### 📈 Data & Analysis
- Earthquake table (sortable & downloadable)
- Magnitude histogram + Magnitude vs. Depth scatterplot

### 📚 Learn Tab
- Explanations of what earthquakes are
- Tectonic movement illustrations
- Pacific Ring of Fire overview
- Safety tips for earthquake preparedness
- Interactive **quiz** to reinforce knowledge

---

## 🛠 Built With

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Pydeck](https://deckgl.readthedocs.io/en/latest/)
- [Seaborn](https://seaborn.pydata.org/) + [Matplotlib](https://matplotlib.org/)
- [USGS Earthquake GeoJSON Feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)

---

## 📦 How to Run Locally

1. **Clone the repository**
```bash
git clone https://github.com/cyruschu430/seismoscope.git
cd seismoscope
