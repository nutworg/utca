import streamlit as st
import pandas as pd
import osmnx as ox
from osmnx import settings
import geopandas as gpd
import pydeck as pdk
from pydeck.types import String
import time
import string

st.title('Utca guesser')
#test

settings.requests_kwargs["verify"]=False

def center(x, y):
    return ((x[0] + y[0]) / 2, (x[1] + y[1]) / 2)



tags = {'highway': True}

@st.cache_data
def load_data():
        streets= ox.geometries_from_place(place_name, tags)
        streets = streets.loc["way"]
        streets = streets[streets["name"].notna()]
        streets=streets[streets.geom_type=="LineString"]
        #st.write(streets["name"])
        streets['points'] = streets.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
        streets['len'] = streets["points"].str.len()
        streets['selected'] = streets.apply(lambda x: x["len"] // 2, axis=1)
        streets['selected2'] = streets.apply(lambda x: center(x['points'][x["len"] // 2], x['points'][x["len"] // 2]), axis=1)
        streets['centroid'] = streets.geometry.centroid
        streets['lon'] = streets.apply(lambda x: x.selected2[0], axis=1)
        streets['lat'] = streets.apply(lambda x: x.selected2[1], axis=1)
        # df = streets[["name", "lat", "lon"]]

        test = gpd.GeoDataFrame()
        test["geometry"] = streets.geometry.centroid
        test["name"] = streets.name
        test['lon'] = streets['lon']
        test['lat'] = streets['lat']
        return test

# def change_data():
#         #st.cache_data.clear()
#         message=st.success('Köszi, adatok betöltése...')
#         message.empty()
#         return load_data()





place_name = st.text_input('Helység neve:')
if not place_name:
  st.warning('Kérlek add meg a betölteni kívánt város nevét!')
  st.stop()

else: 
    test=load_data()

if 'selected' not in st.session_state:
    st.session_state['selected'] = test.sample()


if 'already_done' not in st.session_state:
    st.session_state['already_done'] = pd.DataFrame()

if st.button("Új város"):
    st.cache_data.clear()
    test=load_data()
    st.session_state.selected=test.sample()
    st.session_state['already_done'] = pd.DataFrame()
    st.experimental_rerun()


def check_answer(df,answer):
    if df.iloc[0]["name"]==answer:
        st.session_state.already_done=pd.concat([st.session_state.already_done,st.session_state.selected])
        temp=test.sample()
        st.session_state.selected=temp
        st.success('Helyes válasz!', icon="✅")
        return True
    else:
        st.warning(f'Hibás válasz :( Helyes megoldás: {df.iloc[0]["name"]}', icon="⚠️")
        return False


st.write(st.session_state.selected.iloc[0]["name"])
answer=st.text_input("Utca neve:")
if st.button("Mehet"):
    if check_answer(st.session_state.selected, answer):
        time.sleep(3)
        st.experimental_rerun()

chars = string.ascii_letters + "áéíöüóőúűÁÉÍÖÜÓŐÚŰ1234567890/ "

st.pydeck_chart(pdk.Deck(
    map_style="light_no_labels",
    initial_view_state=pdk.ViewState(
         latitude=st.session_state.selected.iloc[0]["lat"],
         longitude=st.session_state.selected.iloc[0]["lon"],
         zoom=15,
         pitch=10,
    ),
    layers=[
        pdk.Layer(
            "TextLayer",
            st.session_state.already_done,
            pickable=True,
            characterSet=String(chars),
            get_position=["lon", "lat"],  # "coordinates",
            get_text="name",
            get_size=16,
            get_color=[0, 0, 0],
            get_angle=0,
            # Note that string constants in pydeck are explicitly passed as strings
            # This distinguishes them from columns in a data set
            get_text_anchor=String("middle"),
            get_alignment_baseline=String("center")),
        pdk.Layer(
            "ScatterplotLayer",
            st.session_state.selected,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=20,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position="geometry.coordinates",
            get_radius="exits_radius",
            get_fill_color=[255, 140, 0],
            get_line_color=[0, 0, 0],
        ),
        pdk.Layer(
            "ScatterplotLayer",
            st.session_state.already_done,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=20,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position="geometry.coordinates",
            get_radius="exits_radius",
            get_fill_color=[0, 255, 0],
            get_line_color=[0, 0, 0],
        )
    ],
))


