# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 21:09:29 2020

@author: Allan Zhang
"""

import urllib.request
import os
import io
from PIL import Image
import csv

try:
    from xml.etree import cElementTree as ET
except ImportError as e:
    from xml.etree import ElementTree as ET

#Get pano_id of GSV image given lat lon of camera location
def getPanoId(latLon):
    #API call with latlon => returns xml file with data of image including pano_id
    url = "http://maps.google.com/cbk?output=xml&ll=" + str(latLon[0]) + "," + str(latLon[1]) + "&dm=1"
    xml = urllib.request.urlopen(url)
    tree = ET.parse(xml)
    root = tree.getroot()
    pano = {}
    #Find and returns pano_id
    for child in root:
        if child.tag == 'data_properties':
            pano[child.tag] = child.attrib
    return pano['data_properties']['pano_id']

#Get width and height of GSV image given xml data of image
def getWidthHeight(path_to_metadata_xml):
    pano = {}
    pano_xml = open(path_to_metadata_xml, 'rb')
    tree = ET.parse(pano_xml)
    root = tree.getroot()
    #find and return width and height as array
    for child in root:
        if child.tag == 'data_properties':
            pano[child.tag] = child.attrib
    return (int(pano['data_properties']['image_width']),int(pano['data_properties']['image_height']))

def downloadPano():
    #download xml data for image using pano_id to query
    url = "http://maps.google.com/cbk?output=xml&cb_client=maps_sv&hl=en&dm=1&pm=1&ph=1&renderer=cubic,spherical&v=4&panoid="
    xml = urllib.request.urlopen(url + pano_id)
    with open(output_file + ".xml", 'wb') as f:
        for line in xml:
            f.write(line)
    #get width and height of this image
    wh = getWidthHeight(output_file + ".xml")
    image_width = wh[0]
    image_height = wh[1]
    im_dimension = (image_width, image_height)
    #blank canvas to paste tiles
    blank_image = Image.new('RGB', im_dimension, (0, 0, 0, 0))
    
    base_url = 'http://maps.google.com/cbk?'
    
    #Loop through as many tiles as in the image given each tile is 512
    for y in range(int(round(image_height / 512.0))):
        for x in range(int(round(image_width / 512.0))):
            #API call with at specific tile and zoom
            url_param = 'output=tile&zoom=' + str(5) + '&x=' + str(x) + '&y=' + str(
                y) + '&cb_client=maps_sv&fover=2&onerr=3&renderer=spherical&v=4&panoid=' + pano_id
            url = base_url + url_param

            # Open an image, resize it to 512x512, and paste it into a canvas
            req = urllib.request.urlopen(url)
            file = io.BytesIO(req.read())

            im = Image.open(file)
            im = im.resize((512, 512))

            blank_image.paste(im, (512 * x, 512 * y))
    #Save the image
    blank_image.save(output_file + '.jpeg')
    #I changed this 436 from 664 for permission
    os.chmod(output_file + '.jpeg', 436)
    
    
#latlon of camera location 
with open("/home/ndenizturhan/file_end.csv", "r") as f:
    for line in csv.DictReader(f):
        latLon=[float(line["lon"]), float(line["lat"])]
#latLon = [40.77230357827777, -73.91335910964906]
        pano_id = getPanoId(latLon)
#image save destination (added pano_id so that image is called pano_id.jpg)
        output_file = "/home/ndenizturhan/Downloads/pyjava/SingleGSVPanoramaDownload-master/outputpano/" + pano_id

        downloadPano()
