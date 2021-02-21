import streamlit as st
import plotly.express as px

import math
import datetime

import numpy as np
import pandas as pd

import config
import requests
import os

st.set_page_config("Calculateur d'impots",layout='wide')

st.title("Calculateur d'impots")

st.header('Impot sur la fortune immobiliere')

def decoteifi(assets):
    if assets <1300000 or assets >1400000:
        return 0
    else:
        return 17500-(0.0125*assets)


def ifi(assets):
    if assets < 1300000:
        tax = 0
    elif assets <2570000:
        tax = 2500+(assets-1300000)*0.007
        if assets < 1400000:
            tax = tax - decoteifi(assets)
    elif assets < 5000000:
        tax = 11390+(assets-2570000)*0.01
    elif assets < 10000000:
        tax = 35690+(assets-5000000)*0.0125
    else:
        tax = 98190+(assets-10000000)*0.015
    return '{:,.2f}'.format(tax)

assets = st.number_input("Entrez votre patrimoine taxable a l'IFI en millions d'euros",value=2.00,step=0.20,format='%.2f')*1000000

message = "Votre montant d'IFI estime est de "+ifi(assets)+' euros.'
st.subheader(message)


st.header('Impot plus values immobilieres')

col3,col4 = st.beta_columns(2)

with col3:
    pxvente = st.number_input("Entrez votre prix de vente en millions d'euros",value=0.60,step=0.10,format='%.2f')*1000000
with col4:
    pxacquisition = st.number_input("Entrez votre prix d'acquisition en millions d'euros",value=0.30,step=0.10,format='%.2f')*1000000

anneeacqui = st.date_input("Entrez votre date d'acquisition",value=datetime.date(2005,7,10),min_value=datetime.date(2003,7,10))
success = st.checkbox("Bien recu en succession?")

duree = (datetime.date.today()-anneeacqui)
nbyears = duree.days/365

def deduction(price):
    if success==False:
        if nbyears < 5:
            return (0.075*price)
        else:
            return ((0.075+0.15)*price)
    elif nbyears>5:
        return 0.15*price
    else:
        return 0

deduct = deduction(pxacquisition)


ir=0.19
charges = 0.172

def reducir(time):
    if time <6:
        return 0
    elif time<22:
        return 0.06*(time-5)
    elif time==22:
        return 0.06*16+0.04
    else:
        return 1

def reduchar(time):
    if time <6:
        return 0
    elif time<22:
        return 0.0165*(time-5)
    elif time==22:
        return 0.0165*16+0.016
    elif time < 31:
        return (0.0165*16+0.016+0.09*(time-22))
    else:
        return 1

plusvalue = (pxvente - (pxacquisition+deduction(pxacquisition)))


irtax = ir*(1-reducir(math.floor(nbyears)))
chtax = charges*(1-reduchar(math.floor(nbyears)))

totaltax = irtax + chtax

# Plus value immobiliere elevee

def pvelevee(pv):
    if pv < 50000:
        return 0
    elif pv < 60000:
        return 0.02*pv-(60000-pv)/20
    elif pv < 100000:
        return 0.02*pv
    elif pv < 110000:
        return 0.03*pv-(110000-pv)/10
    elif pv < 150000:
        return 0.03*pv
    elif pv < 160000:
        return 0.04*pv-(160000-pv)*15/100
    elif pv < 200000:
        return 0.04*pv
    elif pv < 210000:
        return 0.05*pv - (210000-pv)*20/100
    elif pv < 250000:
        return 0.05*pv
    elif pv < 260000:
        return 0.06*pv - (260000-pv)*25/100
    else:
        return 0.06*pv


totaltax = totaltax*plusvalue+pvelevee(plusvalue)

items = ['Prix achat','Prix vente','Duree detention','Succession','Plus value apres deductions','Deductions','Impot sur le revenu','Charges','Impot plus-values elevees','Total impots']
values = [pxacquisition,pxvente,nbyears,success,plusvalue,deduction(pxacquisition),irtax*plusvalue,chtax*plusvalue,pvelevee(plusvalue),totaltax]

df = pd.DataFrame([values],columns=items)

for col in [0,1,2,4,5,6,7,8,9]:
    df.iloc[:,col] = df.iloc[:,col].apply(lambda x: '{:,.2f}'.format(x))
for col in [3]:
    df.iloc[:,col] = df.iloc[:,col].apply(lambda x: 'Non' if x==0 else 'Oui')

df = pd.DataFrame(df).transpose()
df.columns=['Donnee']
st.table(df)

# gooddf = df.style.format({'Prix achat':'{:,.2f}','Prix vente':'{:,.2f}','Duree detention':'{:,.2f}','Plus value':'{:,.2f}','Dont deductions':'{:,.2f}','IR':'{:,.2%}','Charges':'{:,.2%}','Impot PV elevees':'{:,.2f}','Total impots':'{:,.2f}'})

# st.table(gooddf)

iryears = [ir*(1-reducir(year)) for year in range(31)]
chyears = [charges*(1-reduchar(year)) for year in range(31)]

mychart = pd.DataFrame([iryears,chyears]).transpose()
mychart.columns=['IR','Charges']

fig = px.area(mychart,title="Taux d'imposition")
fig.update_xaxes(title_text='Annees')
fig.update_yaxes(title_text="Taux d'imposition",tickformat='.2%')

st.plotly_chart(fig,use_container_width=True)

st.markdown('Note:')

if deduct == 0:
    st.write('Vous ne beneficiez pas de deductions.')
elif nbyears<5 and success==False:
    st.write('Vous beneficiez de 7.5% de deduction pour frais de notaire soit ', '{:,.2f}'.format(deduct),' euros.')
elif nbyears>5 and success==True:
    st.write('Vous beneficiez de 15% de deduction pour travaux soit ', '{:,.2f}'.format(deduct),' euros au total.')
else:
    st.write('Vous beneficiez de 7.5% de deduction pour frais de notaire et 15% pour travaux soit ', '{:,.2f}'.format(deduct),' euros au total.')
