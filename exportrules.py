import re
import tkinter as tk
from tkinter import filedialog

FIREWALL_RULES_CSV = 'firewall_rules.csv'


def readconfig(rules):
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
                rules[out_rule] = out_rule + "," + out_description
                lookfor = 'rule'
    f.close()


def readrules(rules):
    # read existing rules, to be updated in the next step
    # this allows old rules (no longer relevant in the current configuration) to still be
    # available for matching in Splunk)
    f = open(FIREWALL_RULES_CSV)
    first = True
    for line in f:
        if not first:
            elements = line.split(',')
            rules[elements[0]] = line.strip()
        first = False



def writerules(rules):
    # now write all the rules to a CSV file
    outfile = open(FIREWALL_RULES_CSV, 'w')
    outfile.write('Rule,Description\n')
    for key in rules:
        outfile.write((rules[key]+'\n'))
    outfile.close()


def main():
    rules = dict()

    # read existing rules, so the current items can be added
    # (to ensure old events still have recognised firewall rule descriptions)
    readrules(rules)

    # now read current edgerouter config to update existing rules
    readconfig(rules)
    writerules(rules)


if __name__ == "__main__":
    main()