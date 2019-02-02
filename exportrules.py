import re
rules = list()
lookfor: str = 'rule'     # can be rule or desc

try:
    f = open('config')
except:
    print('could not open file')
    exit()
for line in f:
    line = line.strip()
    if lookfor=='rule':
        strFirst = re.findall('(^set firewall name )(.+)( rule )(.+) action (.+)',line)
        if strFirst.__len__()>0:
            '-- build the string for this rule'
            strRule=strFirst[0][1].strip()+'-'+strFirst[0][3].strip()+'-'+strFirst[0][4][0].upper()
            strDesc=strFirst[0][0] + strFirst[0][1] + strFirst[0][2] + strFirst[0][3] + ' ' + 'description (.+)'
            lookfor='desc'
    else:
        # this line must have the description
        # if it is not there, there is no description and we should continue to the next rule
        Desc = re.findall(strDesc,line)
        if Desc.__len__()>0:
            strDesc = strFirst[0][1].strip() + '-' + Desc[0]
            # strDesc = Desc[0].replace("'","")
            strDesc = strDesc.replace("'","")
        else:
            strDesc=''
        strOutput = strRule+","+strDesc
        rules.append(strOutput)
        lookfor='rule'
f.close()

# now write all the rules to a CSV file
fOut = open('firewall_rules.csv','w')
fOut.write('Rule,Description\n')
for i in range(len(rules)):
    fOut.write(rules[i]+'\n')
fOut.close()