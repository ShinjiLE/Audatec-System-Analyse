#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 21:11:07 2020

@author: shinji
"""

import argparse
import struct
import os
class CRCCalc:
    def __init__(self, polynom = 0x1021, start_val = 0xffff, bitcount = 8):
        self.bitrange = range(bitcount) # 8 Bits
        self.start_val = start_val
        self.crcsum   = self.start_val
        self.polynom = polynom
        self.count = 0
        
    def GenCCITT_CRC16(self, Buffer ):
       #~~ Generierung der CCITT-CRC16 Checksumme  
       for byte in Buffer:
          self.count+=1
          self.crcsum ^= byte << 8
          for bit in self.bitrange: # Schleife für 8 Bits 
             self.crcsum <<= 1
             if self.crcsum & 0x7FFF0000:
                #~~ Es gab einen Uebertrag ins Bit-16
                self.crcsum = (self.crcsum & 0x0000FFFF) ^ self.polynom
                
    def get_crc(self):
        return self.crcsum
    
    def get_count(self):
        return(self.count)
    
    def reset_crc(self):
        self.crcsum = self.start_val
        self.count = 0
                
parser = argparse.ArgumentParser()
parser.add_argument("file", help="Datei die gelesen werden soll")
args = parser.parse_args()
#f = open("/home/shinji/Nextcloud/Rechenwerk/Steuerungstechnik/Geräte und Reglerwerk Teltow/Audatec/Projekte/F60/Strukturdaten/DISK___8.830/X2021480.BDA","rb")

filename, file_extension = os.path.splitext(args.file)

f = open(args.file, "rb")
# check for correct fileextension and use the correct blocksize for padding if required 
if file_extension.lower() in (".sda", ".bda", ".sds", ".bds"):
#   This is a File from a system with floppy
    print("File from Disk")
    media = 'disk'
    block_size = 124
elif file_extension.lower() == '.fex':
#   This is from a Tape ...
    print("File from Tape")
    media = 'tape'
    block_size = 0
    min_block_size = 12 # Scheint zumindest erst mal so
else: 
#   don´t like to process this ...
    exit("Whatever ... this is not a structure file ?!")
    
dst_addr = 0x0000
start_addr = 0x0000
end_adr = 0x0000
block_nummer = 0
range_new = True
range_len = 0
range_num = -1
memory_map = []
datacrc = CRCCalc()
while True: 
    datacrc.reset_crc()
    # ToDo: Das geht doch noch schicker mit der Anzahl der zu lesenden Bytes ?
    try:
        blk_len, dst_addr, dst_fe = struct.unpack('=BHB', f.read(4))
    except :
        print('file read end')
        break
    if not blk_len:
    # EOF
        break
    if ((blk_len < 7) and (dst_fe == 0xff)):
        print("Warning blocklegth {:d}!".format(blk_len))
        blk_len = 7
    data = bytes(f.read(blk_len))
    if(end_adr+1 != dst_addr):
        memory_map.append({})
        start_addr = dst_addr
        range_new = True
        range_num += 1
        range_len = blk_len
        memory_map[range_num]['start_adr'] = start_addr
        memory_map[range_num]['start_block'] = block_nummer
        memory_map[range_num]['FE'] = dst_fe
        memory_map[range_num]['data'] = bytes(data)
    else:
        range_len += blk_len
        memory_map[range_num]['data'] = memory_map[range_num]['data'] + data
    memory_map[range_num]['end_block'] = block_nummer
    end_adr = dst_addr + blk_len - 1
    memory_map[range_num]['end_adr'] = end_adr
    memory_map[range_num]['len'] = range_len
    #memory_map[range_num]['CRC16']=GenCCITT_CRC16()
    datacrc.GenCCITT_CRC16(memory_map[range_num]['data'])
    memory_map[range_num]['CRC16']=datacrc.get_crc()
    if block_size:
        rest = f.read(block_size - blk_len)
    if media == 'tape':
        f.read(1) # Dummy read ...
#   print('Len: {cnt:3d} Addr: 0x{addr:04X} - 0x{addr_e:04X} Station: 0x{station:02X}'.format(cnt=blk_len[0],addr=dst_addr[1]+dst_addr[2]*256,addr_e=dst_addr[1]+dst_addr[2]*256+len-1,station=dst_fe))
    # if range_new | True:
    #     print('BLK: {range_num:3d} / {blk:3d} Len: {cnt:3d} / {rlen:5d} Addr: 0x{addr:04X} - 0x{addr_e:04X} Station: 0x{station:02X} 0x{st_addr:04X}'
    #           .format(blk=block_nummer,
    #                   cnt=blk_len,
    #                   addr=dst_addr,
    #                   addr_e=end_adr,
    #                   station=dst_fe,
    #                   st_addr=start_addr,
    #                   rlen=range_len,
    #                   range_num=range_num))
    #     range_new = False
    if dst_fe == 0xFF:
        
        print("{:03d} (0x{:02X})-> ".format(block_nummer,block_nummer), end='')
        try:
            print("0x{:02X} 0x{:02X} 0x{:02X} 0x{:02X} ".format(data[0],data[1],data[2],data[3]),end='')
            print("0x{:04X} ".format((data[4]+data[5]*256)),end='')
            print("{:5d} ".format((data[6]+data[7]*256)),end='')
            print("0x{:02X} 0x{:02X} 0x{:02X} 0x{:02X} ".format(data[8],data[9],data[10],data[11]),end='')
        except:
            pass
        #for dat in data:
        #    print("0x{:02X} ".format(dat), end='')
            #print("{:c} ".format(dat), end='')
        print("<-")
        
    #     print("-) ", end='')
    #     for dat in rest:
    #         #print("0x{:02X} ".format(dat), end='')
    #         print("{:c} ".format(dat), end='')
    #     print("(-")
    block_nummer += 1
print("Fertig")
for x in memory_map:
    if( x['FE'] != 0xFF ):
        print("ADR: 0x{:04X} - 0x{:04X} FE: 0x{:02X} LEN: {:5d} BLK 0x{:02X} - 0x{:02X} CRC: 0x{:04X}".format(x['start_adr'],x['end_adr'],x['FE'],x['len'],x['start_block'],x['end_block'],x['CRC16']))
f.close()

