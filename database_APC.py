#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  =   'Victor Alulema'
__email__   =   'victor.alulema@epn.edu.ec'

'''
    This code combines the 508 files of the APC database in a single file
    that contains only the performance data.
    White spaces are removed and the new file is well structured.
'''
import numpy as np

def propeller_f(file, prop_name, data):
    file.write('Propeller' + '_' + prop_name)
    file.write('\n')
    for line in range(13,len(data)):
        content = " ".join(data[line,0].split())
        items   = len(content.split(' '))
        if items in [1 , 6]:
            pass
        elif items == 4:
            file.write('RPM' + ' ' + content.split(' ')[-1])
            file.write('\n')
        else:
            if 'V' in content:
                pass
            else:
                file.write(content)
                file.write('\n')
    return

if __name__ == '__main__':
    APC_data     =  np.genfromtxt('APC_RPMRANGE.dat', dtype = np.str)
    propellers   =  np.array(APC_data[:,0] , dtype = np.str)
    database     =  open('Database_APC.txt' , 'w')
    for propeller in propellers:
        prop_name  = 'PER3_' + propeller + '.dat'
        prop_file  = open ( prop_name , 'r')
        prop_data  = np.asarray([line.rstrip().split('(\s+)') for line in prop_file ])
        propeller_f(database, propeller, prop_data)
    database.close()


