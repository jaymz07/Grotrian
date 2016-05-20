# -*- coding: utf-8 -*-
"""
Created on Mon May 16 17:25:10 2016

@author: jaymz_ubuntu
"""

import sys
import copy
import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction

levelWidth = 0.3
labelSpacing=0.1

dataFile = 'data_files/Mg-II.levels'
dataFileSeparator = ','

showElectricDipole =        False
showElectricQuadrupole =    False

showSplittings =        True
exaggerateSplittings =  True
splitMargin = .04

for i in range(0,len(sys.argv)):
    if((sys.argv[i] == '-i' or sys.argv[i]=='--input') and len(sys.argv)>i+1):
        dataFile=sys.argv[i+1]
    elif((sys.argv[i] == '-d' or sys.argv[i]=='--dipole')):
        showElectricDipole = True
    elif((sys.argv[i] == '-q' or sys.argv[i]=='--quadrupole')):
        showElectricQuadrupole = True
    elif((sys.argv[i] == '-l' or sys.argv[i]=='--no-splitting')):
        showSplittings = False
    elif((sys.argv[i] == '-e' or sys.argv[i]=='--no-exaggerate')):
        exaggerateSplittings = False
    elif((sys.argv[i] == '-s' or sys.argv[i]=='--seperator') and len(sys.argv)>i+1):
        dataFileSeparator=sys.argv[i+1]
    elif((sys.argv[i] == '-h' or sys.argv[i]=='--help')):
        print('----------------------------------\nGroutrian diagram generator. Takes input from list of energy levels and outputs an energy level diagram.\n\nCommand line options:\nArgument\t\t\tParameter\t\tInfo\n\
        -i,--input\t\t[file]\t\tInput file.\n\
        -d,--dipole\t\t\t\tShow dipole transitions\n\
        -q,--quadrupole\t\t\t\tShow quadrupole transitions\n\
        -l,--no-splitting\t\t\tDisable level splitting\n\
        -e,--no-exaggerate\t\t\tDisable level splitting exaggeration\n\
        -s,--separator\t\t[Delimiter]\tSpecify custom delimiter character. (Default is \',\')\n\
        -h,--help\t\t\t\tShow this help\n\n----------------------------------\n')
        sys.exit()
        

title = 'Energy Level Diagram for ' + dataFile
scale = 'cm$^{-1}$'
termSymbols = ['S','P','D','F','G','H','I','J','K','L','M','N','O','Q','R']
labelError = False

file = open(dataFile,'r')
minY, maxY, minX, maxX = 0, 0, 0, 0
maxl = 0
yMargin = 0.1

levels = []
transitions = []
splittings = []

##Read data file
for line in file:
    if(len(line)==0):
        continue
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
            elif(vals[0] == '$SPLITSCALE'):
                splitMargin = float(vals[1])
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

##Parse level properties from label
for i in range(0,len(levels)):
    lbl = levels[i]['label']
    if(lbl.count('^') == 1 and lbl.count('_')==1):
        st = lbl
        st=st.split('^')
        
        levels[i]['n']=int(st[0])
        levels[i]['mult']=int(st[1][0])
        levels[i]['j']=Fraction(st[1].split('_')[-1])
        
        hasTerm = False
        for j in range(0,len(termSymbols)):
            if(termSymbols[j] in st[1]):
                levels[i]['l'] = j
                hasTerm = True
        if(not hasTerm):
            levels[i]['l']=-1
        
        xstart = levels[i]['l']+1
        maxl=max(maxl,levels[i]['l'])
        
        levels[i]['s']=(levels[i]['mult']-1)/2
        
        if(levels[i]['mult'] > 1):
            sLbl = str(levels[i]['n']) + '^' + str(levels[i]['mult']) + termSymbols[levels[i]['l']]
            haveLevel = False
            for j in range(0,len(splittings)):
                if(splittings[j]['label'] == sLbl):
                    splittings[j]['levels'].append({'j' : levels[i]['j'], 'energy' : levels[i]['energy']})
                    haveLevel = True
                    break
            if(not haveLevel):
                splittings.append({'label' : sLbl, 'levels' : [{'j' : levels[i]['j'], 'energy' : levels[i]['energy']}] })
        
        levels[i]['xstart']=xstart
        minX=min(xstart,minX)
        maxX=max(xstart,maxX)
        
        if(levels[i]['mult'] not in multiplicities):
            multiplicities.append(levels[i]['mult'])
    else:
        labelError = True
        levels[i]['xstart']=1
        print("Invalid level label encountered. Will not parse state properties")

##Remove level splittings containing only one level and sort remaining levels
count = 0
while(count < len(splittings)):
    if(len(splittings[count]['levels']) <= 1):
        del splittings[count]
    else:
        minE = splittings[count]['levels'][0]['energy']
        maxE = minE
        avgE = 0
        for i in range(0,len(splittings[count]['levels'])):
            eI = splittings[count]['levels'][i]['energy']
            avgE += eI
            minE=min(minE,eI)
            maxE=max(maxE,eI)
            for j in range(i+1,len(splittings[count]['levels'])):
                if(eI > splittings[count]['levels'][j]['energy']):
                    temp = copy.deepcopy(splittings[count]['levels'][i])
                    splittings[count]['levels'][i] = splittings[count]['levels'][j]
                    splittings[count]['levels'][j] = temp
        splittings[count]['width']=maxE-minE
        splittings[count]['avgEn']=avgE/len(splittings[count]['levels'])
        count = count+1
        
if(labelError):
    for lvl in levels:
        lvl['xstart']=1
        

multiplicities.sort()
rangeX = maxX-minX
if(not labelError):
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

##Append wavelength calculation to transition strings, if option set
for trans in transitions:
    if(not trans.has_key('label')):
        if(trans.has_key('show-nm') and not trans['show-nm']):
            continue
        else:
            trans['label']=nmString(trans)
    elif(trans.has_key('show-nm') and trans['show-nm']):
        trans['label']=trans['label'] + ' (' + nmString(trans) +')'

yRange = maxY-minY

def indexSplit(lvl):
    splitIndex = -1
    jInd = -1
    lbl = lvl['label']
    for i in range(0,len(splittings)):
        if(splittings[i]['label'] == lbl.split('_')[0]):
            splitIndex = i
            break
    for i in range(0,len(splittings[splitIndex]['levels'])):
        if(splittings[splitIndex]['levels'][i]['j']==lvl['j']):
            jInd = i
            break
    return [splitIndex, jInd]
    
##Plot level lines
for level in levels:
    lbl = level['label']
    splitIndex = indexSplit(level)[0]
    aPos = (level['xstart']-levelWidth-labelSpacing,level['energy'])
    if(labelError or splitIndex==-1 or not showSplittings):
        plt.plot([level['xstart']-levelWidth,level['xstart']+levelWidth],[level['energy'],level['energy']],'-0')
        if(not labelError):
            plt.annotate('$'+lbl.split('_')[0]+ '_{'+ str(level['j']) + '}$',xy=aPos)
        else:
            plt.annotate(lbl,xy=aPos)
    else:
        split = splittings[splitIndex]
        avgEn = split['avgEn']
        plt.plot([level['xstart']-levelWidth,level['xstart']-levelWidth/2],[avgEn]*2,'-0')
        exScale = 1
        if(exaggerateSplittings and showSplittings):
            exScale = yRange*splitMargin/split['width']
        for i in range(0,len(split['levels'])):
            exEn = (split['levels'][i]['energy'] - avgEn)*exScale + avgEn
            plt.plot([level['xstart']-levelWidth/2,level['xstart']],[avgEn,exEn],'--',color='black')
            plt.plot([level['xstart'],level['xstart']+levelWidth],[exEn]*2,'-0')
            sPos= (level['xstart'],exEn)
            plt.annotate('$j='+ str(split['levels'][i]['j']) +'$',xy=sPos)
        plt.annotate('$'+lbl.split('_')[0]+'$',xy=(aPos[0],avgEn))

##Draw Transition arrows    
for t in transitions:
    indI = indexSplit(levels[t['i']])
    indF = indexSplit(levels[t['f']])
    x=levels[t['i']]['xstart']
    y=levels[t['i']]['energy']
    if(exaggerateSplittings and indI[0] > -1 and showSplittings):
        exScale = 1
        if(exaggerateSplittings):
            exScale = yRange*splitMargin/splittings[indI[0]]['width']
        x += levelWidth/2
        y = (splittings[indI[0]]['levels'][indI[1]]['energy'] - splittings[indI[0]]['avgEn'])*exScale + splittings[indI[0]]['avgEn']
        
    dx = levels[t['f']]['xstart']-x
    dy = levels[t['f']]['energy']-y
    if(exaggerateSplittings and indF[0] > -1 and showSplittings):
        exScale = 1
        if(exaggerateSplittings):
            exScale = yRange*splitMargin/splittings[indF[0]]['width']
        dx += levelWidth/2
        dy = (splittings[indF[0]]['levels'][indF[1]]['energy'] - splittings[indF[0]]['avgEn'])*exScale + splittings[indF[0]]['avgEn'] - y
    dr = np.sqrt(dx**2+dy**2)
    headLength, headWidth = 0.0, 0.00
    tColor = 'red'
    aColor = 'blue'
    if(t.has_key('color')):
        tColor=t['color'].rstrip()
        aColor = tColor
    plt.arrow(x,y,dx-dx/dr*headLength,dy-dy/dr*headLength,head_width=headWidth,head_length=headLength,color=tColor)
    plt.annotate(t['label'],xy=(x+dx/2,y+dy/2),color=aColor)
plt.ylim(minY-yMargin*yRange,maxY+yMargin*yRange)
plt.ylabel(scale)
plt.title(title)
plt.xlim(0,5)
if(not labelError):
    plt.xticks(range(1,6*len(multiplicities)),(termSymbols[0:maxl+1]+[''])*len(multiplicities))
else:
    plt.xticks([1],[''])
for i in range(0,len(multiplicities)-1):
    plt.plot([5*(i+1),5*(i+1)],[minY-yMargin*yRange,maxY+yMargin*yRange],'-0')
plt.show()