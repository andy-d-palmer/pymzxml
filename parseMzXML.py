# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 11:03:26 2015

@author: andrew palmer, palmer@embl.de
Class to load and parses mxXML files using minidom
"""
import base64
import struct
from xml.dom import minidom
import numpy as np
def decode_spectrum(line,precision='32'): # modified from https://code.google.com/p/massspec-toolbox/source/browse/trunk/mzxml/MzXML.py
        decoded = base64.decodestring(line)
        if precision == '32':
            tmp_size = len(decoded)/4
            unpack_format1 = "!%dL" % tmp_size
            unpack_format2 = 'I'
            unpack_format3 = 'f'
        elif precision == '64':
            tmp_size = len(decoded)/8
            unpack_format1 = "!%dQ" % tmp_size
            unpack_format2 = 'L'
            unpack_format3 = 'd'
        idx = 0
        mz_list = []
        intensity_list = []
        for tmp in struct.unpack(unpack_format1,decoded):
            tmp_i = struct.pack(unpack_format2,tmp)
            tmp_f = struct.unpack(unpack_format3,tmp_i)[0]
            if( idx % 2 == 0 ):
                mz_list.append( float(tmp_f) )
            else:
                intensity_list.append( float(tmp_f) )
            idx += 1
        return mz_list,intensity_list
        
def get_top_peaks(mzlist,countlist,n_output):
                # format for output
                n_output = min((n_output,len(mzlist)))
                sortedcount_idx = np.argsort(countlist,axis=-1)
                mzlist = np.asarray(mzlist)[sortedcount_idx[-n_output:]]
                countlist = np.asarray(countlist)[sortedcount_idx[-n_output:]]
                return mzlist,countlist
                
class parseMzXML():
    #Function to unpack a particular scan to mzlist/countlist with accompaying metatdata
    def __init__(self,filename):
        self.doc = minidom.parse(filename)
        self.n_scans = len(self.doc.getElementsByTagName("scan"))
        self.default_precision = "32"
    
    def get_scan_list(self):
        # returns a NodeList that can be interated over to get individual scan instances
        return self.doc.getElementsByTagName("scan")
        
    def get_scan_info(self,scan):
        # Get generic scan info
        scan_info={}
        for attrib in scan.attributes.keys():
            scan_info[attrib] = scan.getAttribute(attrib)
        return scan_info

    def get_peaks(self,scan):
        # get meta-data
        peaks_element = scan.getElementsByTagName('peaks')
        attribs = {}
        for attrib in peaks_element[0].attributes.keys():
            attribs[attrib] = peaks_element[0].getAttribute(attrib)
        if 'precision' not in attribs.keys():
            print 'precision attribute missing from {} - using self.default_precision'
            attribs["precision"] = self.default_precision
        # get actual data
        peak_base64 = peaks_element[0].childNodes[0].nodeValue
        return attribs,peak_base64

    def get_spectrum(self,scan): #get and decode spectrum
        attribs,peak_base64 = self.get_peaks(scan)
        mzlist,countlist = decode_spectrum(peak_base64,precision=attribs["precision"])
        return mzlist,countlist
    