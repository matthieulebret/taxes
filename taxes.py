import streamlit as st
import altair as alt

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

col1,col2 = st.beta_columns(2)

with col1:
    assets = st.number_input("Entrez votre patrimoine taxable a l'IFI en millions d'euros",value=2.00,step=0.20,format='%.2f')*1000000
with col2:
    st.write('')
    st.write("Votre montant d'IFI estime est de ",ifi(assets),' euros.')


st.header('Real estate sales tax')

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
    else:
        return 0

deduct = deduction(pxacquisition)

if deduct == 0:
    st.write('Vous ne beneficiez pas de deductions.')
elif nbyears<5:
    st.write('Vous beneficiez de 7.5% de deduction pour frais de notaire soit ', '{:,.2f}'.format(deduct),' euros.')
else:
    st.write('Vous beneficiez de 7.5% de deduction pour frais de notaire et 15% pour travaux soit ', '{:,.2f}'.format(deduct),' euros au total.')

ir=0.19
charges = 0.172

def reducir(time):
    if time <6:
        return 0
    elif time<22:
        return 0.06*(time-6)
    elif time==22:
        return 0.06*16
    else:
        return 1

def reduchar(time):
    if time <6:
        return 0
    elif time<23:
        return 0.0165*(time-5)
    elif time==23:
        return 0.0165*23+0.016
    elif time < 31:
        return (1-(31-time)*0.09)
    else:
        return 1

plusvalue = (pxvente - (pxacquisition+deduction(pxacquisition)))

st.write("Votre plus value nette s'eleve a ",'{:,.2f}'.format(plusvalue),' euros.')

irtax = ir*reducir(math.floor(nbyears))
chtax = charges*reduchar(math.floor(nbyears))

totaltax = irtax + chtax

st.write("Votre impot s'eleve a ",'{:,.2f}'.format(totaltax*plusvalue),' euros.')
st.write("L'impot sur le revenu correspond a ",'{:,.2f}'.format(irtax*plusvalue),' euros.')
st.write("Les charges sociales correspondent a ",'{:,.2f}'.format(chtax*plusvalue),' euros.')
