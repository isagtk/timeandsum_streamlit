# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 20:31:35 2022

@author: iza
"""

import pandas as pd
import numpy as np
import os
import streamlit as st
#import xlsxwriter
import datetime
import time
from datetime import timedelta
from datetime import datetime as dt
import csv
import plotly.express as px
import io
import webbrowser
import urllib


global uploaded_file

class MySchool():

    def __init__(self):
        self.selection_date=""
        self.selection_group=""
        
        self.add_info(uploaded_file)
        
        
    @st.cache(persist=True)    
    def add_info(self,uploaded_file):
        global df
        global df_info
        
        #Define df
        df=pd.read_excel(uploaded_file, keep_default_na=False, sheet_name='Data', na_values=None)
        df["ID_ROW"] = df.index
        df['Monday_HRS_P']=np.nan
        df['Monday_HRS_F']=np.nan
        df=df[['Monday_Gr', 'Monday_Name', 'Monday_IN_P', 'Monday_OUT_P',
               'Monday_IN_F', 'Monday_OUT_F', 'Tuesday_Gr', 'Tuesday_Name',
               'Tuesday_IN_P', 'Tuesday_OUT_P', 'Tuesday_IN_F', 'Tuesday_OUT_F',
               'Wednesday_Gr', 'Wednesday_Name', 'Wednesday_IN_P', 'Wednesday_OUT_P',
               'Wednesday_IN_F', 'Wednesday_OUT_F', 'Thursday_Gr', 'Thursday_Name',
               'Thursday_IN_P', 'Thursday_OUT_P', 'Thursday_IN_F', 'Thursday_OUT_F',
               'Friday_Gr', 'Friday_Name', 'Friday_IN_P', 'Friday_OUT_P',
               'Friday_IN_F', 'Friday_OUT_F', ' Saturday_Gr', ' Saturday_Name',
               ' Saturday_IN_P', ' Saturday_OUT_P', ' Saturday_IN_F',
               ' Saturday_OUT_F', ' Sunday_Gr', ' Sunday_Name', ' Sunday_IN_P',
               ' Sunday_OUT_P', ' Sunday_IN_F', ' Sunday_OUT_F']]
        print(df.columns)
        df.head()
        
        
        
        #Define df_info
        df_info=pd.read_excel(uploaded_file, keep_default_na=False, sheet_name='Info', na_values=None)
        df_info.head()
        df_info=df_info.dropna(subset=['Name'])        
        
        #Find 2nd week in df
        whereis2week=list(df['Monday_Gr'])
        index2week=whereis2week.index('Monday2_Gr')
        splitindex=index2week
        df1=df.iloc[:splitindex]
        df1.reset_index(inplace=True)
        df1=df1.drop(columns='index')
        df1.head()
        df2=df.iloc[splitindex+1:]
        df2.reset_index(inplace=True)
        df2=df2.drop(columns='index')
        df2=df2.add_suffix('_2')
        
        df2.head()
        df=pd.concat([df1, df2], axis=1)
        
        #Create new format of df
        list_columns=df.columns
        nr_columns=len(df. columns)
        df_days=pd.DataFrame()
        for i in range(0, nr_columns-6, 6):
            df_day=df[[list_columns[i],list_columns[i+1],list_columns[i+2],list_columns[i+3],list_columns[i+4],list_columns[i+5]]]
            day_date=df_day[list_columns[i]].iloc[0]
            day_week=df_day[list_columns[i]].iloc[1]          

            
            df_day=df_day.drop([0,1,2,3])
            df_day.rename(columns = {list_columns[i]:'Group', list_columns[i+1]:'Name', \
                                     list_columns[i+2]:'Assumption_IN', list_columns[i+3]:'Assumption_OUT', \
                                     list_columns[i+4]:'Actual_IN', list_columns[i+5]:'Actual_OUT'}, inplace = True)            
            
            
            df_day=df_day.dropna()
            df_day['Date']=day_date
            #df_day['Day_of_week']=np.where(df_day['Name'].isna(),None,day_week)
            df_day['Day_of_week']=day_week
            df_day['Teacher (y or n)']=np.nan
            df_day['Factor']=np.nan 
            df_day['Price']=np.nan
            df_day['HRS_Assumption']=np.nan
            df_day['Sum_Assumption']=np.nan
            df_day['HRS_Actual']=np.nan
            df_day['Sum_Actual']=np.nan
            df_day['HRS_Delta']=np.nan
            df_day['Sum_Delta']=np.nan
            df_day['Note']=np.nan 
            df_day.reset_index(drop=True, inplace=True)

            df_days=pd.concat([df_days, df_day], axis=0, ignore_index=True)             
            
            
        df_days=df_days[df_days['Name']!='']
        df_days=df_days[['Date', 'Day_of_week', 'Group', 'Name', \
                            'Teacher (y or n)', 'Factor', 'Price', \
                            'Assumption_IN','Assumption_OUT',  'HRS_Assumption', 'Sum_Assumption', \
                            'Actual_IN', 'Actual_OUT', 'HRS_Actual', 'Sum_Actual', \
                           'HRS_Delta', 'Sum_Delta', 'Note']]
        df_days.reset_index(drop=True, inplace=True)
        
        
        #Calculate/add values
        df_days['Teacher (y or n)']=df_days['Name'].map(dict(zip(df_info['Name'],df_info['Teacher (y or n)'])))
        df_days['Price']=df_days['Name'].map(dict(zip(df_info['Name'],df_info['Price'])))
        list_teacher=['y', 'yes', 'Y', 'Yes', 'YES', 'T', 't', 'True', 'Teacher', 'teacher', 'TEACHER']
        df_days['Factor']=np.where(df_days['Teacher (y or n)'].isin(list_teacher),-1,1 )
        df_days['Price']=np.where(df_days['Price'].isnull(),0,df_days['Price'] )        

        if len(df_days)>0:
            for i in range(0,len(df_days.index)):
                bool_empty_Assumption=df_days['Assumption_IN'].iloc[i]=='' or df_days['Assumption_IN'].iloc[i]==0 or df_days['Assumption_OUT'].iloc[i]=='' or df_days['Assumption_OUT'].iloc[i]==0
                print(i)
                print(bool_empty_Assumption)
                if bool_empty_Assumption==False:
                    df_days['HRS_Assumption'].iloc[i]=((pd.to_datetime(str(df_days['Date'].iloc[i]) + ' ' + str(df_days['Assumption_OUT'].iloc[i])))-\
                        (pd.to_datetime(str(df_days['Date'].iloc[i]) + ' ' + str(df_days['Assumption_IN'].iloc[i])))).total_seconds() / 60 / 60
                else:
                    df_days['HRS_Assumption'].iloc[i]=0
                
                if df_days['HRS_Assumption'].iloc[i]<0:
                   df_days['HRS_Assumption'].iloc[i]=0
                   df_days['Note'].iloc[i]='Error: IN later than OUT (Assumption or Actual)'
                else:
                    pass
                
                bool_empty_Actual=df_days['Actual_IN'].iloc[i]=='' or df_days['Actual_IN'].iloc[i]==0 or df_days['Actual_OUT'].iloc[i]=='' or df_days['Actual_OUT'].iloc[i]==0
                print(i)
                print(bool_empty_Actual)
                if bool_empty_Actual==False:
                    df_days['HRS_Actual'].iloc[i]=((pd.to_datetime(str(df_days['Date'].iloc[i]) + ' ' + str(df_days['Actual_OUT'].iloc[i])))-\
                        (pd.to_datetime(str(df_days['Date'].iloc[i]) + ' ' + str(df_days['Actual_IN'].iloc[i])))).total_seconds() / 60 / 60
                else:
                    df_days['HRS_Actual'].iloc[i]=0                
                
                if df_days['HRS_Actual'].iloc[i]<0:
                   df_days['HRS_Actual'].iloc[i]=0
                   df_days['Note'].iloc[i]='Error: IN later than OUT (Assumption or Actual)'
                else:
                    pass
                
        df_days['Sum_Assumption']=df_days['HRS_Assumption']*df_days['Factor']*df_days['Price']
        df_days['Sum_Actual']=df_days['HRS_Actual']*df_days['Factor']*df_days['Price']      
        df_days['HRS_Delta']=df_days['HRS_Actual']-df_days['HRS_Assumption']
        df_days['Sum_Delta']=df_days['HRS_Delta']*df_days['Factor']*df_days['Price']         
        df=df_days
        
        #Print OUTPUT

        df.to_excel("OUTPUT_Myschool.xlsx", sheet_name="Output", index = False)
        return df


    
#ToRun=MySchool()     

def main():
    global uploaded_file
    
    st.title("My School ☀️")

    #======================
    st.markdown("Upload data from")
    page_radionames=['URL', 'Local file']
    page=st.radio('Input', page_radionames, index=1)
    
    
    if page=='URL':
           #url_file=st.text_input(label = "Please enter URL")
           #st.write(url_file)
           #url_file='https://docs.google.com/spreadsheets/d/1PV8NqPZt0GEKVtEk2CcUX876l2qqEYwP5npbLAVk8L8/edit?usp=sharing' 
           url_file='https://docs.google.com/spreadsheets/d/1PV8NqPZt0GEKVtEk2CcUX876l2qqEYwP5npbLAVk8L8/edit#gid=2070559139'
           if  url_file is not None:
                uploaded_file = pd.read_html(url_file)
                shows = pd.read_html(url_file)
           else:
                st.markdown('Error')
            
    else:
           uploaded_file = st.file_uploader("Data for Analysis <<MYDF1.xlsx>>", type='xlsx', accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
    
           if uploaded_file is not None:
            
                file_container2 = st.expander("The file must have: sheet <<Data>> and sheet <<Info>>. Check your uploaded .xlsx")
                shows = pd.read_excel(uploaded_file)
                uploaded_file.seek(0)
                file_container2.write(shows)
                stop_info2=1

           else:
                st.stop()
   
            
    ndf=MySchool()
    df=ndf.add_info(uploaded_file)
    print('Data')
    print(df)
    
    
    
    
    list_name=['All']+list(set(df['Name']))
    selection_name=st.selectbox('Select name:', list_name)
    df.selection_name=selection_name
    
    
   
    if selection_name!='All':
        df.loc[df['Name']==selection_name]
        df1=df.loc[df['Name']==selection_name]
    else:
        df1=df

    
    
    st.subheader('Total')
    sum_f=df1['Sum_Actual'].sum()
    sum_delta=df1['Sum_Delta'].sum()
    sum_p=df1['Sum_Assumption'].sum()
    df1['Total delta']=np.nan
    df1['Total delta'].iloc[0]='Actual - Predicted:'
    df1['Total delta'].iloc[1]=sum_delta
    if len(df) > 0:
        totals = df.groupby("Name", as_index=False).sum()
        
        
        st.metric(label='Delta', value=f"${sum_delta}", delta=None, delta_color="normal", help=None)
        st.metric(label='Actual Sum', value=f"${sum_f}", delta=sum_delta, delta_color="normal", help=None)
        st.metric(label='Actual - Predicted', value=f"${sum_f} - ${sum_p}", delta=None, delta_color="normal", help=None)
        
    form = st.form("my_form")
    
    
    group_list=list(set(df['Group']))
    sum_list=[]
    for group in group_list:
        df_group=df.loc[df['Group']==group]
        sum_i=df_group['Sum_Actual'].sum()
        sum_list.append(sum_i)
    group_count= pd.DataFrame({'Group':group_list,'Actual_Sum':sum_list})     

    
    #================
    st.sidebar.title('Analysis')
    
    
    st.sidebar.subheader('With Selection Generate Output')
    st.sidebar.markdown(selection_name)
    time_str=time.strftime("%Y_%m_%d_%H%M")
    filename="Invoice_"+time_str + '_' + selection_name + '.xlsx'

    buffer = io.BytesIO()    
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df1.to_excel(writer, sheet_name=selection_name, index=False)
        writer.save()
        
        st.sidebar.download_button(
            label="Download Excel Output",
            data=buffer,
            file_name=filename,
            mime="application/vnd.ms-excel",
            )
        
    
    st.sidebar.subheader('Show Graph')
    if st.sidebar.checkbox('Histogram for Groups', False):
        st.markdown('## Actual Sums by Groups')
        fig=px.bar(group_count, x='Group', y='Actual_Sum', color='Actual_Sum', height=500)
        st.plotly_chart(fig)
    #================
if __name__=='__main__':

    main()
