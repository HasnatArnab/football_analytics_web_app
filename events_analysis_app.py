#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 11:42:46 2021

@author: hasnat
"""

from pandas.core.indexes.base import Index
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from LaurieOnTracking import Metrica_IO as mio
from LaurieOnTracking import Metrica_Viz as mviz

#app title
st.title("Football Data Analysis")


#functions
def to_metric_coordinates(data,field_dimen=(106.,68.)):
    #Converts (x,y) positions from Metrica Unit (cartesian) to meters. Origin at the center (0,0)
    x_columns = [c for c in data.columns if c[-1].lower()=="x"]
    y_columns = [c for c in data.columns if c[-1].lower()=="y"]
    data[x_columns]=(data[x_columns]-0.5)*field_dimen[0]
    data[y_columns]=(data[y_columns]-0.5)*field_dimen[1]
    return data

def plot_pitch( field_dimen = (106.0,68.0), field_color ='green', linewidth=2, markersize=20):
    """ plot_pitch
    
    Plots a soccer pitch. All distance units converted to meters.
    
    Parameters
    -----------
        field_dimen: (length, width) of field in meters. Default is (106,68)
        field_color: color of field. options are {'green','white'}
        linewidth  : width of lines. default = 2
        markersize : size of markers (e.g. penalty spot, centre spot, posts). default = 20
        
    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)
    """
    fig,ax = plt.subplots(figsize=(12,8)) # create a figure 
    # decide what color we want the field to be. Default is green, but can also choose white
    if field_color=='green':
        ax.set_facecolor('mediumseagreen')
        lc = 'whitesmoke' # line color
        pc = 'w' # 'spot' colors
    elif field_color=='white':
        lc = 'k'
        pc = 'k'
    # ALL DIMENSIONS IN m
    border_dimen = (3,3) # include a border arround of the field of width 3m
    meters_per_yard = 0.9144 # unit conversion from yards to meters
    half_pitch_length = field_dimen[0]/2. # length of half pitch
    half_pitch_width = field_dimen[1]/2. # width of half pitch
    signs = [-1,1] 
    # Soccer field dimensions typically defined in yards, so we need to convert to meters
    goal_line_width = 8*meters_per_yard
    box_width = 20*meters_per_yard
    box_length = 6*meters_per_yard
    area_width = 44*meters_per_yard
    area_length = 18*meters_per_yard
    penalty_spot = 12*meters_per_yard
    corner_radius = 1*meters_per_yard
    D_length = 8*meters_per_yard
    D_radius = 10*meters_per_yard
    D_pos = 12*meters_per_yard
    centre_circle_radius = 10*meters_per_yard
    # plot half way line # center circle
    ax.plot([0,0],[-half_pitch_width,half_pitch_width],lc,linewidth=linewidth)
    ax.scatter(0.0,0.0,marker='o',facecolor=lc,linewidth=0,s=markersize)
    y = np.linspace(-1,1,50)*centre_circle_radius
    x = np.sqrt(centre_circle_radius**2-y**2)
    ax.plot(x,y,lc,linewidth=linewidth)
    ax.plot(-x,y,lc,linewidth=linewidth)
    for s in signs: # plots each line seperately
        # plot pitch boundary
        ax.plot([-half_pitch_length,half_pitch_length],[s*half_pitch_width,s*half_pitch_width],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length,s*half_pitch_length],[-half_pitch_width,half_pitch_width],lc,linewidth=linewidth)
        # goal posts & line
        ax.plot( [s*half_pitch_length,s*half_pitch_length],[-goal_line_width/2.,goal_line_width/2.],pc+'s',markersize=6*markersize/20.,linewidth=linewidth)
        # 6 yard box
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*box_length],[box_width/2.,box_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*box_length],[-box_width/2.,-box_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length-s*box_length,s*half_pitch_length-s*box_length],[-box_width/2.,box_width/2.],lc,linewidth=linewidth)
        # penalty area
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*area_length],[area_width/2.,area_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length,s*half_pitch_length-s*area_length],[-area_width/2.,-area_width/2.],lc,linewidth=linewidth)
        ax.plot([s*half_pitch_length-s*area_length,s*half_pitch_length-s*area_length],[-area_width/2.,area_width/2.],lc,linewidth=linewidth)
        # penalty spot
        ax.scatter(s*half_pitch_length-s*penalty_spot,0.0,marker='o',facecolor=lc,linewidth=0,s=markersize)
        # corner flags
        y = np.linspace(0,1,50)*corner_radius
        x = np.sqrt(corner_radius**2-y**2)
        ax.plot(s*half_pitch_length-s*x,-half_pitch_width+y,lc,linewidth=linewidth)
        ax.plot(s*half_pitch_length-s*x,half_pitch_width-y,lc,linewidth=linewidth)
        # draw the D
        y = np.linspace(-1,1,50)*D_length # D_length is the chord of the circle that defines the D
        x = np.sqrt(D_radius**2-y**2)+D_pos
        ax.plot(s*half_pitch_length-s*x,y,lc,linewidth=linewidth)
        
    # remove axis labels and ticks
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    # set axis limits
    xmax = field_dimen[0]/2. + border_dimen[0]
    ymax = field_dimen[1]/2. + border_dimen[1]
    ax.set_xlim([-xmax,xmax])
    ax.set_ylim([-ymax,ymax])
    ax.set_axisbelow(True)
    return fig,ax



#setting up datapaths
DATADIR="./sample-data/data"
game_id=int(st.sidebar.selectbox("Select Game ID",("1","2")))
team=st.sidebar.selectbox("Select Team",("Home","Away"))

#loading events from dataset
eventfile='/Sample_Game_%d/Sample_Game_%d_RawEventsData.csv' %(game_id,game_id)
events=pd.read_csv('{}/{}'.format(DATADIR,  eventfile))

#converting the co-ordinates to actual football field sizes
events=mio.to_metric_coordinates(events)


st.write(team,"Team's Events Overview")
#home/away team events
team_events= events[events["Team"]==team]

st.write(team_events['Type'].value_counts())

#shots data exploration
st.write("Event Type Data Exploration")

type=st.selectbox(f"Select {team} team's event type",("SHOT","PASS","RECOVERY","BALL LOST","CHALLENGE","BALL OUT","SET PIECE","FAULT RECEIVED","CARD"))
# shots=events[events['Type']==type]

#exploring "shots" data for now
team_event_type=team_events[team_events.Type==type]
# st.write(team_event_type.head(10))

st.write(f"{team} team's {type} results")
st.write(team_event_type['Subtype'].value_counts())

#showing goals data
if type=="SHOT":
    st.write(f"{team} team's goals data")
    team_goals=team_event_type[team_event_type['Subtype'].str.contains('-GOAL')].copy()
    st.write(team_goals)

st.write("Events Visualization: Goals")

#goals visualizations
team_event_type=team_events[team_events.Type=="SHOT"]
team_goals=team_event_type[team_event_type['Subtype'].str.contains('-GOAL')].copy()
st.write(team_goals)
fig,ax=plot_pitch()

#getting the indexes of goal data rows
index=team_goals.index
condition=team_goals['Subtype'].str.contains('-GOAL')
goal_indices=index[condition]

#plotting goal positions on the pitch
ax.plot(team_goals.loc[goal_indices]['Start X'],events.loc[goal_indices]['Start Y'],'ro')

for i in goal_indices:
    ax.annotate("",xy=events.loc[i][['End X','End Y']], xytext = events.loc[i][['Start X','Start Y']],alpha=0.1,arrowprops=dict(arrowstyle="->",color="r"))


st.pyplot(fig)
#-------------------------------------------------------
st.write(f"Tracking the players: {team} team")
tracking_team=mio.tracking_data(DATADIR,game_id,team)
tracking_team=mio.to_metric_coordinates(tracking_team)

st.write(tracking_team.head())

#plotting tracking data over 60s
#we get 25 observations of players per seccond. so frame count=60*25 = 1500 
st.write("Movement of the player for first 60 seconds")
fig,ax = mviz.plot_pitch()
colors=["r.","g.","b.","k.","c.","m.","y.","coral","cyan","palegreen","hotpink"]
if team=="Home":
    for i in range(1,14):
        ax.plot(tracking_team[f'{team}_{i}_x'].iloc[:1500],tracking_team[f'{team}_{i}_y'].iloc[:1500],colors[i%11],MarkerSize=1)
else:
    for i in range(15,25):
        ax.plot(tracking_team[f'{team}_{i}_x'].iloc[:1500],tracking_team[f'{team}_{i}_y'].iloc[:1500],colors[i%11],MarkerSize=1)
st.pyplot(fig)



#plotting