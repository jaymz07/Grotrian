# -*- coding: utf-8 -*-
"""
Created on Mon May 16 17:25:10 2016

@author: jaymz_ubuntu
"""

import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction

levelWidth = 0.2

levels = []
levels.append(  {'energy' : 0,                  'label' : '1^2S_1/2'})
levels.append(  {'energy' : 10.198806,          'label' : '2^2P_1/2'})
levels.append(  {'energy' : 10.198851,          'label' : '2^2P_3/2'})
levels.append(  {'energy' : 10.19881043960433,  'label' : '2^2S_1/2'})
levels.append(  {'energy' : 12.0874935577,      'label' : '2^2P_1/2'})
levels.append(  {'energy' : 12.0875069990,      'label' : '2^2P_3/2'})
levels.append(  {'energy' : 12.0874948597,      'label' : '2^2S_1/2'})
levels.append(  {'energy' : 12.0875069769,      'label' : '2^2D_3/2'})
levels.append(  {'energy' : 12.0875114568,      'label' : '2^2D_5/2'})

transitions = []
transitions.append( {'i' : 2, 'f' : 0})

for i in range(0,len(levels)):
    st = levels[i]['label']
    st=st.split('^')
    
    levels[i]['n']=int(st[0])
    levels[i]['mult']=int(st[1][0])
    levels[i]['j']=Fraction(st[1].split('_')[-1])
    if('S' in st[1]):
        levels[i]['l']=0
    elif('P' in st[1]):
        levels[i]['l']=1
    elif('D' in st[1]):
        levels[i]['l']=2
    else:
        levels[i]['l']=-1
    
    if(levels[i]['l'] == 0):
        xstart = 1
    elif(levels[i]['l'] == 1):
        xstart = 2
    elif(levels[i]['l'] == 2):
        xstart = 3
    levels[i]['xstart']=xstart
"""
for i in range(0,len(levels)):
    for j in range(i+1,len(levels)):
        delta_j = abs(levels[i]['j']-levels[j]['j'])
        if(delta_j == Fraction(1,1) or delta_j == Fraction(0,1)):
            if()
"""
for level in levels:
    plt.plot([level['xstart']-levelWidth,level['xstart']+levelWidth],[level['energy'],level['energy']],'-0')
for level in levels:
    plt.annotate('$'+level['label'].split('_')[0]+ '_{'+ str(level['j']) + '}$',xy=(level['xstart']+levelWidth,level['energy']))
for t in transitions:
    plt.arrow(levels[t['i']]['xstart'],levels[t['i']]['energy'],levels[t['f']]['xstart']-levels[t['i']]['xstart'],levels[t['f']]['energy']-levels[t['i']]['energy'],head_width=0.1,head_length=.2,color='red')
plt.ylim(-1,15)
plt.xlim(0,5)
plt.xticks([1,2,3],['S','P','D'])
plt.show()