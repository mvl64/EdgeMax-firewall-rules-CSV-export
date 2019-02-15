import re
import tkinter as tk
from tkinter import filedialog

def create_output(match):
    # match is the regular expression match, layout:
    # [0] name
    # [1] rest of the string

    out_string = ''
    items = re.findall('rule (.+) \{\n(.+)action (.+)',match[1])
    if items.__len__() > 0 :
        out_string = match[0]+'-'+items[0][0]+'-'+items[0][2][0].upper()
        items = re.findall('description (.+)',match[1])
        if items.__len__()>0:
            # use the description
            out_string+=","+items[0]
        else:
            out_string+=","
        return out_string

def parseblock(block, rules):
    reName = re.findall('name (.+) \{', block)
    reRules = re.findall(' rule (.+) {', block)
    reActions = re.findall(' action (.+)\n', block)
    reDescriptions = re.findall(' description (.+)\n', block)
    do = 0  #do: description offset. This is used because there is not always a description of the ruleset.
            # In case there isn't, the do = 0!
    if reDescriptions.__len__()>reRules.__len__():
        do = 1

    #build the rule list
    for i in range(0, reRules.__len__()):
        out_rule = reName[0]+'-'+reRules[i]+'-'+reActions[i][0].upper()+','+reName[0]+'-'+reDescriptions[i+do].replace('"','')
        rules.append(out_rule)


def read_config_boot(rules):
    # read file into buffer
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    buffer = ''
    blockmatching = False
    i = 0

    try:
        f = open(file_path)
    except FileNotFoundError:
        print('Could not open file!')
        exit()
    for line in f:
        # line = line.strip()
        i+=1
        if blockmatching:
            if line == '}':
                parseblock(block, rules)
            else:
                block+=line

        match =re.findall(' name (.+) \{', line)
        if match.__len__()>0:
            if blockmatching:
                # this is the end of the block
                parseblock(block, rules)
            # this is a firewall rule name - start storing the text block for parsing
            rulesetname = match[0]
            block = line
            blockmatching = True

def readrules(rules):
    lookfor: str = 'rule'       # can be rule or description
    searchpattern = ''          # pattern to find the description for the rule we just found
    rule_elements = ''          # elements of the regular expression
    lines = 0                   # how many lines have we tried to find a matching description
    out_description = ''        # for output file: description
    out_rule = ''               # for output file: rule

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
            rule_elements = re.findall('(^set firewall name )(.+)( rule )(.+) action (.+)', line)
            if rule_elements.__len__() > 0:
                '-- build the string for this rule'
                out_rule = rule_elements[0][1].strip() + '-' + rule_elements[0][3].strip() + '-' + rule_elements[0][4][0].upper()
                searchpattern = rule_elements[0][0] + rule_elements[0][1] + rule_elements[0][2] + rule_elements[0][
                    3] + ' ' + 'description (.+)'
                lookfor = 'description'
                lines = 0
                out_description = ''
        else:
            # now search for the description - this may appear in the next line, or a bit further down ...
            # if not found after 4 lines, we'll assume there is no description and continue searching for the next rule
            rule_description = re.findall(searchpattern, line)
            if rule_description.__len__() > 0:
                out_description = rule_elements[0][1].strip() + '-' + rule_description[0]
                out_description = out_description.replace("'", "")
            else:
                # not yet found, search in next line
                lines += 1
                if lines > 2:
                    out_description = '-'
            if out_description.__len__() > 0:
                rules.append(out_rule + "," + out_description)
                lookfor = 'rule'
    f.close()


def writerules(rules):
    # now write all the rules to a CSV file
    outfile = open('firewall_rules.csv', 'w')
    outfile.write('Rule,Description\n')
    for i in range(len(rules)):
        outfile.write(rules[i] + '\n')
    outfile.close()


def main():
    rules = list()
    read_config_boot(rules)
    # readrules(rules)
    writerules(rules)


if __name__ == "__main__":
    main()