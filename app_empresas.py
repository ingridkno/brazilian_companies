import folium
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd

from shapely import wkt

gdf=pd.read_csv(r'./files/estados_n_empresas.csv')
st.dataframe(gdf.head())

df_state_atictivities_size= pd.read_csv(r'./files/empresas_acustica_atividades_mapa_v2_porte.csv')
st.dataframe(df_state_atictivities_size.head())

dict_porte={1.0:'Size not informed', 3.0:'Small size', 5.0:'Others sizes'}


#Page structure
st.title('Brazilian Companies')
st.sidebar.subheader('audio, acoustics, sound and vibration')

all_msg = 'All'

cnaes = pd.read_csv(r'./files/cnaes_acustica.csv')
activities = cnaes['desc_activity'].tolist()
activity_desc = st.sidebar.selectbox('Choose activity',[all_msg] + activities)

if activity_desc==all_msg:
    cnae_code = cnaes.loc[:, 'cnae_code'].tolist()
    df_filtered = df_state_atictivities_size.copy()
else:
    cnae_code = cnaes.loc[cnaes['desc_activity']==activity_desc, 'cnae_code'].tolist()
    df_filtered = df_state_atictivities_size[df_state_atictivities_size[str(cnae_code[0])]==1]

st.text(cnae_code)
st.dataframe(df_filtered)

lista_state= [all_msg] + gdf['uf'].unique().tolist()
state_option = st.sidebar.selectbox('Choose state',lista_state)

if state_option==all_msg:
    zoom=4
else:
    df_filtered = df_filtered[df_filtered['uf']==state_option].copy()
    zoom=5.5
    
    
df_filtered = df_filtered.groupby(['uf','porte']).sum()[['cnpj_basico']].reset_index()

#import numpy as np
df_filtered = pd.pivot_table(df_filtered, values='cnpj_basico', index='uf', columns='porte')
df_filtered = df_filtered.rename(columns=dict_porte)
df_filtered['All sizes']= df_filtered.sum(axis=1)

st.dataframe(df_filtered)#, aggfunc=np.sum))
df_filtered = df_filtered.merge(gdf, left_on='uf', right_on = 'UF_05')

st.dataframe(df_filtered)
df_cards = df_filtered[df_filtered.columns[:4]].sum().astype(int)
st.dataframe(df_cards)#.astype(int))

st.text(int(df_cards['All sizes']))

col1, col2, col3, col4 = st.columns(4)
col1.metric("All sizes companies", str(df_cards['All sizes']))

pct_small=str(int(100*(df_cards['Small size']/df_cards['All sizes'])))
col2.metric("Small size", str(df_cards['Small size']), pct_small+'%')

pct_others = str(int(100*(df_cards['Others sizes']/df_cards['All sizes'])))
col3.metric("Other sizes", str(df_cards['Others sizes']), pct_others+'%')

pct_notinformed = str(int(100*(df_cards['Size not informed']/df_cards['All sizes'])))
col4.metric("Not informed", str(df_cards['Size not informed']), pct_notinformed+'%')

#st.text(df_filtered.columns)



#st.dataframe(gdf)
df_filtered['geometry'] = df_filtered['geometry'].apply(wkt.loads)
count_map = gpd.GeoDataFrame(df_filtered, geometry='geometry', crs='epsg:4326')

x=count_map['geometry'].centroid.x.mean()
y=count_map['geometry'].centroid.y.mean()


bounds = count_map['geometry'].bounds

#st.text(bounds)
#st.text(bounds['miny'].min())

sw =[bounds['miny'].min(), bounds['minx'].min()]
ne = [bounds['maxy'].max(), bounds['maxy'].max()]


m = folium.Map(location=[y, x], zoom_start = zoom, tiles=None,overlay=False) #tiles=None)#'CartoDB positron',overlay=True)#tiles='CartoDB positron')

#m.fit_bounds([ne, sw])


for column_name in ['All sizes','Small size','Others sizes', 'Size not informed']:
    

    myscale = (count_map[column_name].quantile((0,0.1,0.75,0.9,0.98,1))).tolist()
    feature_group = folium.FeatureGroup(name=column_name,overlay=False).add_to(m)

    # Set up Choropleth map
    choropleth1 = folium.Choropleth(
    geo_data=count_map,
    data=count_map,
    columns=['uf',column_name],
    key_on="feature.properties.uf",
    fill_color='YlGnBu',
    fill_opacity=1,
    line_opacity=0.2,
    threshold_scale=myscale,
    legend_name="Number of Companies ("+column_name+')',
    smooth_factor=0,
    Highlight= True,
    line_color = "#0000",
    name = column_name,
    show=True,
    #overlay=False,
    nan_fill_color = "White"
    ).geojson.add_to(feature_group)#add_to(m)

    style_function = lambda x: {'fillColor': '#ffffff',
                                'color':'#000000',
                                'fillOpacity': 0.1,
                                'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000',
                                    'color':'#000000',
                                    'fillOpacity': 0.50,
                                    'weight': 0.1}
    NIL = folium.features.GeoJson(
        count_map,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['uf',column_name],
            aliases=['State: ','Number of Companies: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    ).add_to(choropleth1)


    #m.add_child(NIL)
    #m.keep_in_front(NIL)


folium.TileLayer('cartodbpositron',overlay=True,name="Map").add_to(m)
folium.LayerControl(collapsed=False).add_to(m)


folium_static(m)
