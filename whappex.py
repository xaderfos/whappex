# Copyright 2021 xaderfos (https://github.com/xaderfos)

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys

if len(sys.argv) != 2:
    print("Please provide a path to the exported txt file")
    exit(0)

import re
import pathlib
from datetime import datetime, timedelta

head='''
<!doctype html>
<html lang="en">
    <head>
    <meta charset="utf-8">
    <title>WhatsApp export</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
    <style>
        img {
            max-width: 200px;
            max-height: 200px;
        }
    </style>
    </head>
    <body>
'''

rest='''
    </body>
</html>
'''

# Regular expresions
mediaOmitted=r"^([0-9]+/[0-9]+/[0-9]+), ([0-9]{2}:[0-9]{2}) - .*: <Media omitted>$"
hyperlinks=r"(http[s]?://\S*)"

# Paths
pathToChatFile = pathlib.Path(sys.argv[1]).expanduser()
parentDir = pathlib.Path(pathToChatFile).parent
pathToOutputFile = pathlib.Path(f"{parentDir.absolute()}{pathlib.os.sep}index.html")

# Collect all media files in parentDir and subfolders
media = []
for p in parentDir.glob("**/*"):
    # Supporting only images for now
    if p.suffix in ['.jpg', '.jpeg']:
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        mtime = mtime - timedelta(seconds=mtime.second, microseconds=mtime.microsecond)
        media.append({"t": mtime, "f": p})

# Just keeping things sorted...
def d_key (d):
    return d["t"]

media.sort(key=d_key)

with open(pathToChatFile, "r") as chat:
    with open(pathToOutputFile, 'w') as fh:
        # Write the header of the HTML file
        fh.write(f"{head}\n")
        # Read the chat line by line
        for line in chat:
            x = re.search(mediaOmitted, line)
            # We got a match for <Media omitted>
            if x is not None:
                # Extract datetime
                date = x.group(1)
                time = x.group(2)
                dt = datetime.strptime(f"{date} {time}", '%m/%d/%y %H:%M')
                # Try to find any media file with the same datetime
                # FIXME items with the same datetime will overwrite
                for m in media:
                    if m["t"] == dt:
                        # Replace the media omitted tag with the actual media file.
                        line = line.replace("<Media omitted>", f'</p>\n<a href="{m["f"].name}" target="_blank"><img src="{m["f"].name}" alt="{m["f"].name}"/></a>')
                        # remove matched items to narrow down our problem space
                        media.remove(m)
            else:
                # enable hyperlinks
                line = re.sub(hyperlinks, r'<a href="\1">\1</a>', line)
            # Append each line to output
            fh.write(f"<p>{line[:-1]}</p>\n")
        # Write the rest the HTML file
        fh.write(f"{rest}\n")
