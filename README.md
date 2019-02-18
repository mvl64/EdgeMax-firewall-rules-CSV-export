This python script parses the "human readable" format of the Edgerouter configuration,
file "/config/congif.boot" and outputs a CSV file listing all the firewall rules in the format:

<rulesetname>-<interface>-<action>, <rulesetname>-<interface>-<description>

For example:
GUEST_IN-10-D,GUEST_IN-Drop invalid state

This allows easy reporting in Splunk, using firewall rule names and descriptions, rather than cryptic codes (the first part of the line, before the comma)