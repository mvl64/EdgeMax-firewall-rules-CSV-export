import re
import tkinter as tk
from tkinter import filedialog

rules = list()
lookfor: str = 'rule'  # can be rule or desc
strDescPattern = ''
strFirst = ''
LinesSearchedForDesc = 0
strDesc = ''
strRule = ''

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

try:
    f = open(file_path)
except FileNotFoundError:
    print('Could not open file "config"')
    exit()
for line in f:
    line = line.strip()
    if lookfor == 'rule':
        strFirst = re.findall('(^set firewall name )(.+)( rule )(.+) action (.+)', line)
        if strFirst.__len__() > 0:
            '-- build the string for this rule'
            strRule = strFirst[0][1].strip() + '-' + strFirst[0][3].strip() + '-' + strFirst[0][4][0].upper()
            strDescPattern = strFirst[0][0] + strFirst[0][1] + strFirst[0][2] + strFirst[0][
                3] + ' ' + 'description (.+)'
            lookfor = 'desc'
            LinesSearchedForDesc = 0
            strDesc = ''
    else:
        # now search for the description - this may appear in the next line, or a bit further down ...
        # if not found after 4 lines, we'll assume there is no description and continue searching for the next rule
        Desc = re.findall(strDescPattern, line)
        if Desc.__len__() > 0:
            strDesc = strFirst[0][1].strip() + '-' + Desc[0]
            strDesc = strDesc.replace("'", "")
        else:
            # not yet found, search in next line
            LinesSearchedForDesc += 1
            if LinesSearchedForDesc > 2:
                strDesc = '-'
        if strDesc.__len__() > 0:
            strOutput = strRule + "," + strDesc
            rules.append(strOutput)
            lookfor = 'rule'
f.close()

# now write all the rules to a CSV file
fOut = open('firewall_rules.csv', 'w')
fOut.write('Rule,Description\n')
for i in range(len(rules)):
    fOut.write(rules[i] + '\n')
fOut.close()
