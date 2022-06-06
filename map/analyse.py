import json
import PIL
from PIL import *
from PIL import Image, ImageDraw, ImageOps
import svgwrite
import svgutils

jf = open('nodes.json', 'r')
json = json.load(jf)

minx = 99999
miny = 99999
minz = 99999
maxx = -99999
maxy = -99999
maxz = -99999

for area in json:
    minD = area["DimensionMin"]
    maxD = area["DimensionMax"]

    if minD["X"] < minx:
        minx = minD["X"]
    if minD["Y"] < miny:
        miny = minD["Y"]
    if minD["Z"] < minz:
        minz = minD["Z"]
    
    if maxD["X"] > maxx:
        maxx = maxD["X"]
    if maxD["Y"] > maxy:
        maxy = maxD["Y"]
    if maxD["Z"] > maxz:
        maxz = maxD["Z"]

print("Min(" + str(minx) + ", " + str(miny) + ", " + str(minz) + ")")
print("Max(" + str(maxx) + ", " + str(maxy) + ", " + str(maxz) + ")")

map = Image.open("heightmap.png")
map = ImageOps.flip(map)
svg_map = svgwrite.Drawing('map.svg', profile='full')
svg_map.add(svg_map.rect(insert=(0, 0), size=(maxx - minx, maxy - miny), fill='#000'))
svg_map_gps = svgwrite.Drawing('map_gps.svg', profile='full')
svg_map_norm = svgwrite.Drawing('map_norm.svg', profile='full')
svg_map_traf = svgwrite.Drawing('map_traf.svg', profile='full')

fac = 10

svg_style = """ <style type="text/css"><![CDATA[
       .route {
         stroke: #a04bed;
         fill: red;
       }
    ]]></style>
    """

svg_wat = '<svg baseProfile="full" viewBox="0 0 ' + str((maxx - minx) * fac) + ' ' + str((maxy - miny) * fac) + '" height="' + str(100 * fac) + '%" version="1.1" width="' + str(100 * fac) + """%" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">
                <defs />\n"""
svg_nogps = '</svg><svg baseProfile="full" viewBox="0 0 ' + str((maxx - minx) * fac) + ' ' + str((maxy - miny) * fac) + '" height="' + str(100 * fac) + '%" version="1.1" width="' + str(100 * fac) + """%" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">\n"""
svg_road = '</svg><svg baseProfile="full" viewBox="0 0 ' + str((maxx - minx) * fac) + ' ' + str((maxy - miny) * fac) + '" height="' + str(100 * fac) + '%" version="1.1" width="' + str(100 * fac) + """%" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">\n"""
svg_tl = '</svg><svg baseProfile="full" viewBox="0 0 ' + str((maxx - minx) * fac) + ' ' + str((maxy - miny) * fac) + '" height="' + str(100 * fac) + '%" version="1.1" width="' + str(100 * fac) + """%" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">\n"""


sgw = 0
sgwa = ["#000000", "#AAAAAA", "#FFFFFF"]

def getCol(aId):
    aId = int(aId / 255 * 75)
    return aId

for area in json:
    draw = ImageDraw.Draw(map)
    cval = getCol(area["AreaId"])
    draw.rectangle((area["DimensionMin"]["X"] - minx, area["DimensionMin"]["Y"] - miny, area["DimensionMax"]["X"] - minx, area["DimensionMax"]["Y"] - miny), fill=(cval, cval, cval))

    areamap = Image.new('RGBA', (int(area["DimensionMax"]["X"] - area["DimensionMin"]["X"]), int(area["DimensionMax"]["Y"] - area["DimensionMin"]["Y"])), (0, 0, 0, 0))
    if sgw < 2:
        sgw += 1
    else:
        sgw = 0
    
    for node in area["Nodes"]:
        nx = node["Position"]["X"] - minx
        ny = node["Position"]["Y"] - miny
        for conNode in node["ConnectedNodes"]:
            cx = conNode["Node"]["Position"]["X"] - minx
            cy = conNode["Node"]["Position"]["Y"] - miny
            draw = ImageDraw.Draw(map)

            drawArea = ImageDraw.Draw(areamap)

            fclass = str(node["Position"]["X"]) + '+' + str(node["Position"]["Y"]) + '+' + str(node["Position"]["Z"]) + '>' + str(conNode["Node"]["Position"]["X"]) + '+' + str(conNode["Node"]["Position"]["Y"]) + '+' + str(conNode["Node"]["Position"]["Z"])
            sclass = str(conNode["Node"]["Position"]["X"]) + '+' + str(conNode["Node"]["Position"]["Y"]) + '+' + str(conNode["Node"]["Position"]["Z"]) + '>' + str(node["Position"]["X"]) + '+' + str(node["Position"]["Y"]) + '+' + str(node["Position"]["Z"])

            if conNode["Node"]["IsOnWater"] == True:
                draw.line((nx, ny, cx, cy), fill="#536c99", width=10)
                svg_wat += '                <line class="' + "road" + fclass + " " + sclass + '" stroke="#536c99" stroke-width="' + str(10 * fac) + '" x1="' + str(nx * fac) + '" x2="' + str(cx * fac) + '" y1="' + str(ny * fac) + '" y2="' + str(cy * fac) + '" />\n'

                drawArea.line((int(nx + minx - area["DimensionMin"]["X"]), int(ny + miny - area["DimensionMin"]["Y"]), int(cx + minx - area["DimensionMin"]["X"]), int(cy + miny - area["DimensionMin"]["Y"])), fill="#536c99", width=10)
            elif conNode["Node"]["IsValidForGps"] == False:
                draw.line((nx, ny, cx, cy), fill="#555555", width=10)
                svg_nogps += '              <line class="' + "road" +  fclass + " " + sclass + '" stroke="#555555" stroke-width="' + str(10 * fac) + '" x1="' + str(nx * fac) + '" x2="' + str(cx * fac) + '" y1="' + str(ny * fac) + '" y2="' + str(cy * fac) + '" />\n'

                drawArea.line((int(nx + minx - area["DimensionMin"]["X"]), int(ny + miny - area["DimensionMin"]["Y"]), int(cx + minx - area["DimensionMin"]["X"]), int(cy + miny - area["DimensionMin"]["Y"])), fill="#555555", width=10)
            else:
                draw.line((nx, ny, cx, cy), fill="#999999", width=10)
                svg_road += '               <line class="' + "road" +  fclass + " " + sclass + '" stroke="#999999" stroke-width="' + str(10 * fac) + '" x1="' + str(nx * fac) + '" x2="' + str(cx * fac) + '" y1="' + str(ny * fac) + '" y2="' + str(cy * fac) + '" />\n'
                
                drawArea.line((int(nx + minx - area["DimensionMin"]["X"]), int(ny + miny - area["DimensionMin"]["Y"]), int(cx + minx - area["DimensionMin"]["X"]), int(cy + miny - area["DimensionMin"]["Y"])), fill="#999999", width=10)
        
        if node["TrafficlightExists"] == True:
            draw.ellipse((nx - 5, ny - 5, nx + 5, ny + 5), fill="#ff0000")
            svg_tl += '             <circle cx="' + str(nx * fac) + '" cy="' + str(ny * fac) + '" r="' + str(5 * fac) + '" fill="#ff0000" />\n'

        drawArea.ellipse((int(nx + minx - area["DimensionMin"]["X"] - 5), int(ny + miny - area["DimensionMin"]["Y"] - 5), int(nx + minx - area["DimensionMin"]["X"] + 5), int(ny + miny - area["DimensionMin"]["Y"] + 5)), fill="#00FFFF")
    
    areamap = ImageOps.flip(areamap)
    areamap.save("areas/" + str(area["AreaId"]) + ".png")

map = ImageOps.flip(map)
map.save("map.png")

bef = """<!doctype html>
<html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: black;
                overflow: hidden;
            }
            svg {
                display: flex;""" + '\n             height: ' + str(1000 * fac) + 'px;               width: ' + str(1000 * fac) + 'px; ' + """
                margin-left: 0;
                position: absolute;""" + '              top: calc(' + str(-1000 * fac) + 'px + 50vh);' + """
                left: calc(0px + 50vw);
            }
            input {
                opacity: 0;
                -webkit-appearence: none;
                color: white;
                z-index: 999999;
                background: white;
            }
            input > * {
                color: white;
                z-index: 999999;
            }
            .route {
                stroke: #a04bed;
            }
        </style>
    </head>
    <body onload="ol()">
        <script>
            function ol() {
                var svgs = document.getElementsByTagName('svg');
                for(i = 0; i < svgs.length; i++) {
                    svgs[i].setAttribute("transform", "scale(1 -1)"); //rotate3d(1, 0, 0, 60deg) rotateZ(0deg)");
                }
            }
            function change() {
                var vals = document.getElementById("cords").value;
                if(vals.split(" ").length == 3) {
                    var valx = vals.split(" ")[0];
                    var valy = vals.split(" ")[1];
                    var valR = vals.split(" ")[2];
                    var svgs = document.getElementsByTagName('svg');
                    for(i = 0; i < svgs.length; i++) {
                        svgs[i].style.top = \"""" + 'calc(' + str(-1000 * fac) + 'px + " + valy + "px + 50vh)"' + """;
                        svgs[i].style.left = "calc(-" + valx + "px + 50vw)";
                    }
                }
            }
        </script>
        <input type="text" id="cords" onkeyup="change()" value="">
        """
aft = """
        </svg>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    </body>
</html>"""

html = bef + svg_wat + svg_road + svg_nogps + svg_tl + aft

file = open("index.html", "w")
file.write(html)
file.close()