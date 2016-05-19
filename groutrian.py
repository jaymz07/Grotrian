# -*- coding: utf-8 -*-
"""
Created on Mon May 16 17:25:10 2016

@author: jaymz_ubuntu
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction

levelWidth = 0.2
labelSpacing=.45

dataFile = 'data_files/Mg-II.levels'
dataFileSeparator = ','

showElectricDipole =        False
showElectricQuadrupole =    False

for i in range(0,len(sys.argv)):
    if((sys.argv[i] == '-i' or sys.argv[i]=='--input') and len(sys.argv)>i+1):
        dataFile=sys.argv[i+1]
    elif((sys.argv[i] == '-d' or sys.argv[i]=='--dipole')):
        showElectricDipole = True
    elif((sys.argv[i] == '-q' or sys.argv[i]=='--quadrupole')):
        showElectricQuadrupole = True
    elif((sys.argv[i] == '-s' or sys.argv[i]=='--seperator') and len(sys.argv)>i+1):
        dataFileSeparator=sys.argv[i+1]
    elif((sys.argv[i] == '-h' or sys.argv[i]=='--help')):
        print('----------------------------------\nGroutrian diagram generator. Takes input from list of energy levels and outputs an energy level diagram.\n\nCommand line options:\nArgument\t\t\tParameter\t\tInfo\n\
        -i,--input\t\t[file]\t\tInput file.\n\
        -d,--dipole\t\t\t\tShow dipole transitions\n\
        -q,--quadrupole\t\t\t\tShow quadrupole transitions\n\
        -s,--separator\t\t[Delimiter]\tSpecify custom delimiter character. (Default is \',\')\n\
        -h,--help\t\t\t\tShow this help\n\n----------------------------------\n')
        sys.exit()
        

title = 'Energy Level Diagram for ' + dataFile
scale = 'cm$^{-1}$'
termSymbols = ['S','P','D','F','G','H','I','J','K','L','M','N','O','P','Q','R']

file = open(dataFile,'r')
minY, maxY, minX, maxX = 0, 0, 0, 0
maxl = 0
yMargin = 0.1

levels = []
transitions = []
for line in file:
    if(len(line)>=11 and line[0:11] == '$TRANSITION'):
        ln = line.split(dataFileSeparator)
        transitions.append({'i': int(ln[1]), 'f': int(ln[2])})
        if(len(ln)>3):
            for part in ln:
                command=part.split('=')
                if(command[0]=='$LABEL'):
                    transitions[-1]['label']=command[1]
                elif(command[0]=='$COLOR'):
                    transitions[-1]['color']=command[1]
                elif(command[0]=='$SHOW-NM'):
                    if(command[1].rstrip()=='1' or command[1].rstrip().lower()=='t'):
                        transitions[-1]['show-nm']=True
                    else:
                        transitions[-1]['show-nm']=False
    elif(line[0] == '$'):
        ln = line.split(dataFileSeparator)
        for command in ln:  
            vals = command.split("=")
            if(len(command)==0):
                continue
            if(vals[0] == '$TITLE'):
                title = vals[1]
            elif(vals[0] == '$SCALE'):
                scale = vals[1]
            else:
                print('Invalid Command encountered data file' + dataFile)
                print('---->' + line)
    else:
        ln = line.split(dataFileSeparator)
        if(len(ln[0])==0):
            continue
        v=float(ln[0])
        levels.append({'energy' : v, 'label' : ln[1]})
        minY = min(v,minY)
        maxY = max(v,maxY)
file.close()
multiplicities=[]

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
    elif('F' in st[1]):
        levels[i]['l']=3
    else:
        levels[i]['l']=-1
    
    if(levels[i]['l'] == 0):
        xstart = 1
    elif(levels[i]['l'] == 1):
        xstart = 2
    elif(levels[i]['l'] == 2):
        xstart = 3
    elif(levels[i]['l'] == 3):
        xstart = 4
    maxl=max(maxl,levels[i]['l'])
    
    levels[i]['s']=(levels[i]['mult']-1)/2
        
    levels[i]['xstart']=xstart
    minX=min(xstart,minX)
    maxX=max(xstart,maxX)
    
    if(levels[i]['mult'] not in multiplicities):
        multiplicities.append(levels[i]['mult'])

multiplicities.sort()
rangeX = maxX-minX
for l in levels:
    l['xstart']+=(rangeX + 1)*multiplicities.index(l['mult'])
    maxX=max(maxX,l['xstart'])
    
    
if(showElectricDipole):
    for i in range(0,len(levels)):
        for j in range(i+1,len(levels)):
            delta_j = abs(levels[i]['j']-levels[j]['j'])
            if(delta_j == Fraction(1,1)):
                if(abs(levels[i]['l']-levels[j]['l'])==1):
                    if(levels[i]['s']==levels[j]['s']):
                        transitions.append({'i' : i, 'f' : j})
                    
if(showElectricQuadrupole):
    for i in range(0,len(levels)):
        for j in range(i+1,len(levels)):
            delta_j = abs(levels[i]['j']-levels[j]['j'])
            if(delta_j == Fraction(2,1) or delta_j == Fraction(0,1)):
                if(abs(levels[i]['l']-levels[j]['l'])==2):
                    if(abs(levels[i]['s']-levels[j]['s'])==1.0):
                        transitions.append({'i' : i, 'f' : j})

def nmString(transition):
    return str(int(1239.8393589807376/abs(levels[trans['i']]['energy'] - levels[trans['f']]['energy']))) + 'nm'

for trans in transitions:
    if(not trans.has_key('label')):
        if(trans.has_key('show-nm') and not trans['show-nm']):
            continue
        else:
            trans['label']=nmString(trans)
    elif(trans.has_key('show-nm') and trans['show-nm']):
        trans['label']=trans['label'] + ' (' + nmString(trans) +')'

for level in levels:
    plt.plot([level['xstart']-levelWidth,level['xstart']+levelWidth],[level['energy'],level['energy']],'-0')
for level in levels:
    plt.annotate('$'+level['label'].split('_')[0]+ '_{'+ str(level['j']) + '}$',xy=(level['xstart']-levelWidth-labelSpacing,level['energy']))
for t in transitions:
    x=levels[t['i']]['xstart']
    y=levels[t['i']]['energy']
    dx = levels[t['f']]['xstart']-levels[t['i']]['xstart']
    dy = levels[t['f']]['energy']-levels[t['i']]['energy']
    dr = np.sqrt(dx**2+dy**2)
    headLength, headWidth = 0.0, 0.00
    tColor = 'red'
    aColor = 'blue'
    if(t.has_key('color')):
        tColor=t['color'].rstrip()
        aColor = tColor
    plt.arrow(x,y,dx-dx/dr*headLength,dy-dy/dr*headLength,head_width=headWidth,head_length=headLength,color=tColor)
    plt.annotate(t['label'],xy=(x+dx/2,y+dy/2),color=aColor)
yRange = maxY-minY
plt.ylim(minY-yMargin*yRange,maxY+yMargin*yRange)
plt.ylabel(scale)
plt.title(title)
plt.xlim(0,5)
plt.xticks(range(1,6*len(multiplicities)),(termSymbols[0:maxl+1]+[''])*len(multiplicities))
for i in range(0,len(multiplicities)-1):
    plt.plot([5*(i+1),5*(i+1)],[minY-yMargin*yRange,maxY+yMargin*yRange],'-0')
plt.show()