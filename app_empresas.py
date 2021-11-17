#PACKAGES

import folium
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
from shapely import wkt

#-----------------------------------------------------------------------------------------------------
##FUNCTIONS
#activity filter
def activity_filter(activity_desc, cnaes, df_state_atictivities_size, all_msg):

    #dataframe filtered if all activities are chosen 
    if activity_desc==all_msg:
        cnae_code = cnaes.loc[:, 'cnae_code'].tolist()
        df_filtered = df_state_atictivities_size.copy()
        cnae_message = '**Activity:** All audio, acoustics, sound and vibration activities'
    #dataframe filtered if just one activity is chosen
    else:
        cnae_code = cnaes.loc[cnaes['desc_activity']==activity_desc, 'cnae_code'].tolist()
        df_filtered = df_state_atictivities_size[df_state_atictivities_size[str(cnae_code[0])]==1]
        cnae_message = "**Activity:** " +activity_desc.capitalize() 
     
    return(df_filtered, cnae_code, cnae_message)
  
#state filter  
def state_filter(df_filtered, state_option, all_msg):
    #dataframe filtered if all states are chosen 
    if state_option==all_msg:
        zoom=4 #zoom_start
        state_message='**State:** All Brazilian States'
    #dataframe filtered if just one state is chosen
    else:
        df_filtered = df_filtered[df_filtered['uf']==state_option].copy()
        zoom=5.5 #zoom start for geo map
        state_message= '**State: **' +state_option
    return(df_filtered, state_message, zoom)

#quantity and percentage companies in the cards
def percentage_df(column, df_cards):
    absolute_number = df_cards[column]
    percentage=str(int(100*(df_cards[column]/df_cards['All sizes'])))
    return absolute_number, percentage
    
 
#dataframe filtered ploted in the map
def map_plot(df_filtered, count_map):

    x=count_map['geometry'].centroid.x.mean()
    y=count_map['geometry'].centroid.y.mean()

    m = folium.Map(location=[y, x], zoom_start = zoom, tiles=None,overlay=False) #tiles=None)#'CartoDB positron',overlay=True)#tiles='CartoDB positron')

    for column_name in ['All sizes','Small size','Other sizes', 'Size not informed']:
        

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

    folium.TileLayer('cartodbpositron',overlay=True,name="Map").add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    folium_static(m)


#----------------------------------------------------------------------------------------------------- 
#DATAFRAMES
#states geo dataset
gdf=pd.read_csv(r'./files/estados_n_empresas.csv')
#st.dataframe(gdf.head())

#active companies quantity in Brazil grouped by uf, city, size and acoustic activity 
df_state_atictivities_size= pd.read_csv(r'./files/empresas_acustica_atividades_mapa_v2_porte.csv')
#st.dataframe(df_state_atictivities_size.head())

#dictionary for size 
dict_porte={1.0:'Size not informed', 3.0:'Small size', 5.0:'Other sizes'}

#activity code dataset (acoustics cnaes)
cnaes = pd.read_csv(r'./files/acoustics_activities_code.csv')
activities = cnaes['desc_activity'].tolist()


#-----------------------------------------------------------------------------------------------------
#PAGE STRUCTURE
st.title('Brazilian Companies')

# url_tdc='https://thedevconf.com/img/logos/logo-tdc-horizontal-navbar-inverse.png'
# st.sidebar.image(url_tdc)

st.sidebar.subheader('audio, acoustics, sound and vibration')

#FILTERS
#activity filter sidebar
all_msg = 'All'
activity_desc = st.sidebar.selectbox('Choose activity',[all_msg] + activities)

lista_state= [all_msg] + gdf['uf'].unique().tolist()
state_option = st.sidebar.selectbox('Choose state',lista_state)

#filtering by activity
df_filtered, cnae_code, cnae_message = activity_filter(activity_desc, cnaes, df_state_atictivities_size, all_msg)
#st.text(cnae_code)
#st.dataframe(df_filtered)

#filtering by state   
df_filtered, state_message, zoom = state_filter(df_filtered, state_option, all_msg)

ingrid_photo = 'https://media-exp1.licdn.com/dms/image/C4D03AQH_InG-xiedOA/profile-displayphoto-shrink_800_800/0/1615148707112?e=1642636800&v=beta&t=KVBHsx89CGR_PJGGob87UdRSJD9hsJQbtulcajoIGeg'
_,col1,col2, _ = st.sidebar.columns(4)
col1.image(ingrid_photo)
url='https://www.linkedin.com/in/ingrid-knochenhauer/'
col1.markdown("[Ingrid](url)")

nickolas_photo = 'https://media-exp1.licdn.com/dms/image/C4E03AQEUkRjeGzF2NA/profile-displayphoto-shrink_400_400/0/1537832523370?e=1642636800&v=beta&t=MbtUAuZtNLDPIVSKrVJ_2MzCq9aAfN56-9pChivl7Uw'
col2.image(nickolas_photo)
url='https://www.linkedin.com/in/nickolas-s-mendes/'
col2.markdown("[Nickolas](url)")
    
#dataframe grouped by state and activity chosen in the filter
df_filtered = df_filtered.groupby(['uf','porte']).sum()[['cnpj_basico']].reset_index()
#dataframe organized by state and size
df_filtered = pd.pivot_table(df_filtered, values='cnpj_basico', index='uf', columns='porte')
df_filtered = df_filtered.rename(columns=dict_porte)
#column with sum of sizes
df_filtered['All sizes']= df_filtered.sum(axis=1)
#st.dataframe(df_filtered)

#dataframe filtered and organized merging with geolocation (dataframe gdf)
df_filtered = df_filtered.merge(gdf, left_on='uf', right_on = 'UF_05')
#st.dataframe(df_filtered)

#card numbers with companies quantity
df_cards = df_filtered[df_filtered.columns[:4]].sum().astype(int)
#st.dataframe(df_cards)#.astype(int))

#Chosen activity and state
st.write(cnae_message)
st.write(state_message)

#Quantity and percentage companies in the cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("All sizes companies", str(df_cards['All sizes']))

column_names = ['Small size', 'Other sizes', 'Size not informed']
columns = [col2, col3, col4]
for col, col_name in zip(columns, column_names):
    absolute_number, percentage = percentage_df(col_name, df_cards)
    col.metric(col_name, str(absolute_number), percentage+'%')

#st.dataframe(gdf)
df_filtered['geometry'] = df_filtered['geometry'].apply(wkt.loads)
count_map = gpd.GeoDataFrame(df_filtered, geometry='geometry', crs='epsg:4326')

#plotting dataframe filteres
map_plot(df_filtered, count_map)

url = 'https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj'
st.markdown("[Data](url) from 15/10/2021")
