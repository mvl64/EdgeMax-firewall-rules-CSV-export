import re
import tkinter as tk
from tkinter import filedialog

def ReadRules( rules ):
    lookfor: str = 'rule'  # can be rule or desc
    strDescPattern = ''  # pattern to find the description for the rule we just found
    re_elements = ''  # elements of the regular expression
    LinesSearchedForDesc = 0  # how many lines have we tried to find a matching description
    strDesc = ''  # for output file: description
    strRule = ''  # for output file: rule

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    try:
        f = open(file_path)
    except FileNotFoundError:
        print('Could not open file!')
        exit()
    for line in f:
        line = line.strip()
        if lookfor == 'rule':
            re_elements = re.findall('(^set firewall name )(.+)( rule )(.+) action (.+)', line)
            if re_elements.__len__() > 0:
                '-- build the string for this rule'
                strRule = re_elements[0][1].strip() + '-' + re_elements[0][3].strip() + '-' + re_elements[0][4][0].upper()
                strDescPattern = re_elements[0][0] + re_elements[0][1] + re_elements[0][2] + re_elements[0][
                    3] + ' ' + 'description (.+)'
                lookfor = 'desc'
                LinesSearchedForDesc = 0
                strDesc = ''
        else:
            # now search for the description - this may appear in the next line, or a bit further down ...
            # if not found after 4 lines, we'll assume there is no description and continue searching for the next rule
            Desc = re.findall(strDescPattern, line)
            if Desc.__len__() > 0:
                strDesc = re_elements[0][1].strip() + '-' + Desc[0]
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

def WriteRules(rules):
    # now write all the rules to a CSV file
    fOut = open('firewall_rules.csv', 'w')
    fOut.write('Rule,Description\n')
    for i in range(len(rules)):
        fOut.write(rules[i] + '\n')
    fOut.close()

def main():
    rules = list()
    ReadRules(rules)
    WriteRules(rules)

if __name__ == "__main__":
    main()