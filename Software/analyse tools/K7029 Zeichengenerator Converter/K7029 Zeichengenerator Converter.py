# -*- coding: utf-8 -*-
"""
Spyder Editor

Konvertiert Zeichengenerator EPROM der Anschlusssteuerung Bildschirm K7029 in einzelne Zeichen PNGs
Cheap and crazy solution ... many things are hardwired , but works for me ...
"""
from PIL import Image
#import os
#Ausgabebereich der Zeichen
Char_Start = 0
Char_End = 256
#Zeichen größer in Pixel x,y
Char_Size = (7,9)
#Char_per_page_line = 15
#Char_scale_page = 5
#Char_size_scaled = tuple([Char_scale_page*x for x in Char_Size])
#Char_page_pos = (0,0)+Char_size_scaled
#Page_size=( ( Char_per_page_line * ( Char_Size[ 0 ] + 3 ) )*Char_scale_page, round(((Char_End - Char_Start)/ Char_per_page_line)*(Char_Size[1] + 5 ))*Char_scale_page )
Zeichen = ord('A')

#Page_Image = Image.new("1", Page_size)

#Quellverzeichnis der EPROMs
EPROM_BASE = "/home/shinji/Rechenwerk/Steuerungstechnik/Geräte und Reglerwerk Teltow/Audatec/Software/KLAUCK/ABS/"
#Ausgabeverzeichnis für PNGs 
#Muss bereits existieren ... faulheit siegt 
OUT_BASE = EPROM_BASE+"Zeichen/"
#EPROM Dateinamen -> A5x folgt der Bezeichnung aus der Betriebsdoku K1520 Heft 15 Seite 15 
A51_EPROM_FN = "K7029I A51.ROM"
A52_EPROM_FN = "K7029M A52.ROM"
A53_EPROM_FN = "K7029A A53.ROM"

A51_file = open(EPROM_BASE+A51_EPROM_FN,"rb")
A51_data = A51_file.read()
A51_file.close()

A52_file = open(EPROM_BASE+A52_EPROM_FN,"rb")
A52_data = A52_file.read()
A52_file.close()

A53_file = open(EPROM_BASE+A53_EPROM_FN,"rb")
A53_data = A53_file.read()
A53_file.close()

#Reihenfolge wie die Zeilen des Zeichens in den EPROMs angeordnet sind 
#Betriebsdoku K1520 Heft 15  Seite 13 und 14
pattern = [(A53_data,1),
           (A53_data,0),
           (A52_data,3),
           (A52_data,2),
           (A52_data,1),
           (A52_data,0),
           (A51_data,3),
           (A51_data,2),
           (A51_data,1)]

for Zeichen in range(Char_Start,Char_End):

    character_bytes=[]
    for i in pattern:
        character_bytes.append(i[ 0 ][ ( Zeichen << 2 ) + i[ 1 ] ] >> 1)
    character=[]
    for line in character_bytes:
        for lpxc in range(6,-1,-1):
            character.append(( line >> (lpxc) ) & 0x01)
        print("{0:07b}".format( line ).replace('0', ' ').replace('1', 'O') )
    
    character_image = Image.new("1", Char_Size)
    character_image.putdata(character)
    character_image.save(OUT_BASE+"Zeichen_{0:03d}.png".format(Zeichen))
#    Page_Image.paste(character_image.resize(Char_size_scaled),Char_page_pos)
    character_image.close()
#Page_Image.show()
                     