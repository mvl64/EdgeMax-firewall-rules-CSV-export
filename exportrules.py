import re
import os
import tkinter as tk
from tkinter import filedialog


FIREWALL_RULES_CSV = 'firewall_rules.csv'


def parseblock(block, rules):
    re_name = re.findall('name (.+) {', block)
    re_rules = re.findall(' rule (.+) {', block)
    re_actions = re.findall(' action (.+)\n', block)
    re_descriptions = re.findall(' description (.+)\n', block)
    # do: description offset. This is used because there is not always a description of the ruleset.
    # In case there isn't, the do = 0!
    do = re_descriptions.__len__() - re_rules.__len__()

    # build the rule list
    for i in range(0, re_rules.__len__()):
        out_rule = re_name[0]+'-'+re_rules[i]+'-'+re_actions[i][0].upper()
        out_description = re_name[0]+'-'+re_descriptions[i+do].replace('"', '')
        rules[out_rule] = out_rule + ',' + out_description


def read_config_boot(file_path, rules):
    # read file into buffer
    block = ''
    blockmatching = False
    i = 0

    try:
        f = open(file_path)
    except FileNotFoundError:
        print('Could not open file!')
        exit()
    for line in f:
        i += 1
        if blockmatching:
            if line == '}':
                parseblock(block, rules)
            else:
                block += line

        match = re.findall(' name (.+) {', line)
        if match.__len__() > 0:
            if blockmatching:
                # this is the end of the block
                parseblock(block, rules)
            # this is a firewall rule name - start storing the text block for parsing
            block = line
            blockmatching = True
    f.close()
    return True


def readconfig(file_path, rules):
    lookfor: str = 'rule'       # can be rule or description
    searchpattern = ''          # pattern to find the description for the rule we just found
    rule_elements = ''          # elements of the regular expression
    lines = 0                   # how many lines have we tried to find a matching description
    out_description = ''        # for output file: description
    out_rule = ''               # for output file: rule

    try:
        f = open(file_path)
    except FileNotFoundError:
        print('Could not open file!')
        return False
    for line in f:
        line = line.strip()
        if lookfor == 'rule':
            rule_elements = re.findall('(^set firewall name )(.+)( rule )(.+) action (.+)', line)
            if rule_elements.__len__() > 0:
                '-- build the string for this rule'
                out_rule = rule_elements[0][1].strip() + '-' + rule_elements[0][3].strip() + '-' \
                           + rule_elements[0][4][0].upper()
                searchpattern = rule_elements[0][0] + rule_elements[0][1] + rule_elements[0][2] + \
                                rule_elements[0][3] + ' ' + 'description (.+)'
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
                rules[out_rule] = out_rule + "," + out_description
                lookfor = 'rule'
    f.close()
    return True


def getfilename():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path


def readrules(directory, rules):
    # read existing rules, to be updated in the next step
    # this allows old rules (no longer relevant in the current configuration) to still be
    # available for matching in Splunk)
    f = open(directory + '/' + FIREWALL_RULES_CSV)
    first = True
    for line in f:
        if not first:
            elements = line.split(',')
            rules[elements[0]] = line.strip()
        first = False


def writerules(directory, rules):
    # now write all the rules to a CSV file
    outfile = open(directory + '/' + FIREWALL_RULES_CSV, 'w')
    outfile.write('Rule,Description\n')
    for key in rules:
        outfile.write((rules[key]+'\n'))
    outfile.close()


def main():
    rules = dict()
    file_path = getfilename()
    if file_path == '':
        exit()

    directory = os.path.dirname(file_path)

    # read existing rules, so the current items can be added
    # (to ensure old events still have recognised firewall rule descriptions)
    readrules(directory, rules)

    # now read current edgerouter config to update existing rules
    if read_config_boot(file_path, rules,):
        writerules(directory, rules)


if __name__ == "__main__":
    main()