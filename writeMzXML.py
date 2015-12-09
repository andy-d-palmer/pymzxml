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
def encode_spectrum(mzs,counts,precision='64'): # modified from https://code.google.com/p/massspec-toolbox/source/browse/trunk/mzxml/MzXML.py
        # interlace mzs/counts
        import base64
        if precision == '32':
            tmp_size = 4*(2*len(mzs))/4.
            pack_format1 = "!%dL" % tmp_size
            pack_format2 = '<I'
            pack_format3 = '<f'
        elif precision == '64':
            tmp_size = 8*(2*len(mzs))/8.
            pack_format1 = "!%dQ" % tmp_size
            pack_format2 = 'L'
            pack_format3 = 'd'
        tmp_list = []
        str_to_encode=''
        for m,c in zip(mzs,counts):
            for idx in range(2):
                if idx==0:
                    tmp_f = m
                else:
                    tmp_f = c
                tmp_i  = struct.pack(pack_format3,tmp_f)
                tmp = struct.unpack(pack_format2,tmp_i)[0]
                tmp_list.append(tmp)
        str_to_encode += struct.pack(pack_format1,*tmp_list)
        b64encoded = base64.b64encode(str_to_encode)
        return b64encoded
        
def write_scan(self,buffer,scanNumber,mzList,countList,rt,polarity,msLevel,collisionEnergy,precursorIntensity=[],precursorMz=[]): #get and decode spectrum
        # currently only suppports centroided data
        peaksCount = len(mzList)
        lowMz=mzList[0]
        highMz=mzList[-1]
        basePeakMz=mzList[np.argmax(countList)]
        basePeakIntensity=np.max(countList)
        totIonCurrent=np.sum(countList)
        peakPrecision = mzList.dtype #should be bit count 32/64
        peak_base = ecode_spectrum(mzList,countlist,precision=peakPrecision)
        if mslevel>1: assert precursor != []
        scan_head  = "<scan num=\"{}\" centroided=\"1\" retentionTime=\"{}\" polarity=\"{}\" msLevel=\"{}\" collisionEnergy=\"{}\" peaksCount=\"{}\" lowMz=\"{}\" highMz=\"{}\" basePeakMz=\"{}\" basePeakIntensity=\"{}\" totIonCurrent=\"{}\"> ".format(scanNumber,rt,polarity,msLevel,collisionEnergy,peaksCount,lowMz,highMz,basePeakMz,basePeakIntensity,totIonCurrent)
        peaks      = "<peaks precision=\"{}\" byteOrder=\"network\" pairOrder=\"m/z-int\">{}</peaks> " .format(peaksCount,peakPrecision,peak_base)
        scan_tail  = "</scan>"
        if mslevel==1:
            scan_text  = "\n".join((scan_head,peaks,scan_tail))
        if mslevel==2:
            prec = "<precursorMz precursorIntensity=\"{}\">{}</precursorMz>".format(precursorIntensity,precursorMz)
            scan_text  = "\n".join((scan_head,prec,peaks,scan_tail))
        buffer.write(scan_text)

                
class writeMzXML():
    #Function to unpack a particular scan to mzlist/countlist with accompaying metatdata
    def __init__(self,filename):
        self.filename = filename
        self.scan_list = []

    def add_scan(self,mzs,counts,polarity,scan_num,mslevel,collisionEnergy,rt=0,precursorIntensity=[],precursorMz=[]):
        scan = {"scan_num":scan_num,
                "mzs":mzs,
                "counts":counts,
                "rt":rt,
                "polarity":polarity,
                "mslevel":mslevel,
                "collisionEnergy":collisionEnergy,
                "precursorIntensity":precursorIntensity,
                "precursorMz":precursorMz
                }
        self.scan_list.append(scan)

    def write_mzxml(self):
        with open(self.filename) as f:
            for scan in self.scan_list:
                write_scan(f,scan['scan_num'],scan["mzs"],scan["counts"],scan["rt"],scan["polarity"],scan["mslevel"],scan["collisionEnergy"],scan["precursorIntensity"],scan[precursorMz])


