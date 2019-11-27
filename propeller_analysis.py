#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__  =   'Victor Alulema'
__email__   =   'victor.alulema@epn.edu.ec'

import numpy as np
import pandas as pd 
import matplotlib.cm as cm
from matplotlib import rcParams
import matplotlib.pyplot as plt

rcParams['text.latex.unicode']=True
plt.rc('font', family='serif')

class Propellers:
    def database(self):
        '''
        This function represents the database
        as a dictionary
        '''
        prop_data  = open('Database_APC.txt', 'r')
        propellers = np.asarray([line.rstrip().split('(\s)') for line in prop_data ])
        prop_items = []
        prop_name  = []
        prop_rpm   = []
        for index , propeller in enumerate(propellers):
            content = propeller[0].split(' ')
            items   = len(content)
            if items == 1:
                prop_items.append(index)
                prop_name.append(content[0])
            elif items == 2:
                prop_rpm.append(index)           
        prop_rpm  = np.array(prop_rpm  , dtype = np.int)
        database = {}
        for index , prop in enumerate(prop_items):
            if index == len(prop_items) - 1:
                pass
            else:
                indexes = np.arange(np.where(prop_rpm == prop_items[index] + 1)[0][0] ,
                                    np.where(prop_rpm == prop_items[index + 1] + 1)[0][0])
                RPM  = {}
                for item , value in enumerate(indexes):
                    if item == len(indexes) - 1:
                        pass
                    else:
                        l_bound = prop_rpm[value] + 1
                        u_bound = prop_rpm[indexes[item + 1]]
                        data = []
                        for i in range(l_bound , u_bound):
                            data.append(propellers[i][0].split(' '))
                        RPM[propellers[prop_rpm[value]][0]] = np.array(data , dtype = np.float64)
                database[prop_name[index]] = RPM
        return database
    def all_propellers(self):
        '''
        Returns the names of all
        propellers in the database
        '''
        return Propellers.database(self).keys()
    def info_propeller(self , propeller):
        '''
        Returns the RPM values for
        a given propeller
        '''
        return dict(Propellers.database(self)[propeller].items()).keys()
    def interpolate(self , x1 , x3 , y1 , y3 , x2):
        ''' Interpolate values '''
        y2 = (((x2 - x1) * (y3 - y1)) / (x3 - x1)) + y1 
        return y2
    def propeller_selection(self , speed , P_req , SI = False):
        if SI == False:
            pass
        elif SI == True:
            speed = speed * 2.23694
            P_req = P_req / 745.7 #0.22480
        ''' Propeller selection '''
        database = Propellers.database(self)
        propellers_selected = []
        for key in database.keys():
            data = dict(database[key].items())
            for item in data.keys():
                prop_data = data[item]
                for i , j in enumerate(prop_data[:,0]):
                    if i == len(prop_data[:,0]) - 1:
                        pass
                    else:
                        p1 = prop_data[:,-3][i] * prop_data[:,2][i]
                        p2 = prop_data[:,-3][i+1] * prop_data[:,2][i+1]
                        if ((speed >= prop_data[:,0][i] and
                             speed <= prop_data[:,0][i + 1]) and
                           ((P_req >= p1 and
                             P_req <= p2 or
                            (P_req <= p1 and
                             P_req >= p2)))):
                            x1     = prop_data[:,0][i]
                            x3     = prop_data[:,0][i + 1]
                            prop_1 = prop_data[i][1:]
                            prop_2 = prop_data[i + 1][1:]
                            propellers_selected.append(key)
                            propellers_selected.append(item)
                            propellers_selected.append(speed)
                            for index , value in enumerate(prop_1):
                                y1 = value
                                y3 = prop_2[index]
                                y2 = Propellers.interpolate(self, x1 , x3 , y1 , y3 , speed)
                                propellers_selected.append(y2)
                                
        propellers = np.asarray(propellers_selected)
        propellers = propellers.reshape((int(len(propellers_selected) / 10) , 10))
        prop_name  = propellers[:,0]
        prop_rpm   = propellers[:,1]
        prop_V     = np.array(propellers[:,2] , dtype = np.float)
        prop_J     = np.array(propellers[:,3] , dtype = np.float)
        prop_eff   = np.array(propellers[:,4] , dtype = np.float)
        prop_Ct    = np.array(propellers[:,5] , dtype = np.float)
        prop_Cp    = np.array(propellers[:,6] , dtype = np.float)
        prop_PWR   = np.array(propellers[:,7] , dtype = np.float)
        prop_t     = np.array(propellers[:,8] , dtype = np.float)
        prop_T     = np.array(propellers[:,9] , dtype = np.float)
        if SI == False:
            file_name = 'V' + str(round(speed , 2)) + '__' + 'T' + \
                        str(round(T_req , 2)) + '__' + 'English' + '.csv'
        elif SI == True:
            prop_V   = prop_V / 2.23694
            prop_PWR = prop_PWR * 745.7
            prop_t   = prop_t * 0.112985
            prop_T   = prop_T * 4.44822
            speed    = speed / 2.23694
            P_req    = P_req  * 745.7
            file_name = 'V' + str(round(speed , 2)) + '__' + 'T' + \
                        str(round(P_req , 2)) + '__' + 'International' + '.csv'
            
        output = np.array([prop_name , prop_rpm ,
                               prop_V    , prop_J   , prop_eff ,
                               prop_Ct   , prop_Cp  , prop_PWR ,
                               prop_t    , prop_T]).T
        indexes = np.argsort(output[:,4])
        output  = output[indexes[::-1]]
        pd.DataFrame(output).to_csv(file_name ,header = None , index = None)
        return   
    
    def performance_propeller(self , propeller):
        '''
        Returns plots of performance
        for all RPM values
        '''
        data     = dict(Propellers.database(self)[propeller].items())
        colors   = cm.jet(np.linspace(0, 1, len(data.keys())))
        keys     = sorted([int(i[4:]) for i in list(data.keys())])
        keys     = ['RPM' + ' ' + str(i) for i in keys]
        fig      = plt.figure(figsize = (8.5 , 7))
        for c , key in enumerate(keys):
            a1 = fig.add_subplot(221)
            a1.plot(data[str(key)][:,1] , data[str(key)][:,2] ,
                    color = colors[c] ,
                    linewidth = 0.9   ,
                    label = key)
            a1.spines['right'].set_visible(False)
            a1.spines['top'].set_visible(False)
            a1.set_ylabel('efficiency')
            a2 = fig.add_subplot(222)
            a2.plot(data[str(key)][:,1] , data[str(key)][:,5] ,
                    color = colors[c] , 
                    linewidth = 0.9   ,
                    label = key)
            a2.spines['right'].set_visible(False)
            a2.spines['top'].set_visible(False)
            a2.set_ylabel('Power [Hp]')
            a3 = fig.add_subplot(223)
            a3.plot(data[str(key)][:,1] , data[str(key)][:,6] ,
                    color = colors[c] , 
                    linewidth = 0.9   ,
                    label = key)
            a3.spines['right'].set_visible(False)
            a3.spines['top'].set_visible(False)
            a3.set_xlabel('J')
            a3.set_ylabel('Torque [in-lbf]')
            a3.legend(ncol = 2 , loc = 'upper right' ,
                      fontsize = 7 , frameon = False)
            a4 = fig.add_subplot(224)
            a4.plot(data[str(key)][:,1] , data[str(key)][:,7] ,
                    color = colors[c] , 
                    linewidth = 0.9   ,
                    label = key)
            a4.spines['right'].set_visible(False)
            a4.spines['top'].set_visible(False)
            a4.set_xlabel('J')
            a4.set_ylabel('Thrust [lbf]')
            
        fig.tight_layout()
        plt.show()
        return
    
    def compare_propellers(self , propellers , RPM_range):
        data     = Propellers.database(self)
        colors   = cm.jet(np.linspace(0, 1, len(RPM_range)))
        fig      = plt.figure(figsize = (8.5 , 7))
        a1 = fig.add_subplot(221)
        a2 = fig.add_subplot(222)
        a3 = fig.add_subplot(223)
        a4 = fig.add_subplot(224)
        a1.spines['right'].set_visible(False)
        a1.spines['top'].set_visible(False)
        a1.set_ylabel('efficiency')
        a2.spines['right'].set_visible(False)
        a2.spines['top'].set_visible(False)
        a2.set_ylabel('Power [Hp]')
        a3.spines['right'].set_visible(False)
        a3.spines['top'].set_visible(False)
        a3.set_xlabel('J')
        a3.set_ylabel('Torque [in-lbf]')
        a4.spines['right'].set_visible(False)
        a4.spines['top'].set_visible(False)
        a4.set_xlabel('J')
        a4.set_ylabel('Thrust [lbf]')
        for propeller in propellers:
            for color , rpm in enumerate(RPM_range):
                   a1.plot(data[propeller][rpm][:,1] , data[propeller][rpm][:,2] ,
                           linewidth = 0.9)
                   a2.plot(data[propeller][rpm][:,1] , data[propeller][rpm][:,5] ,
                           linewidth = 0.9)      
                   a3.plot(data[propeller][rpm][:,1] , data[propeller][rpm][:,6] ,
                           linewidth = 0.9   ,
                           label = propeller + ' ' + rpm)
                   a4.plot(data[propeller][rpm][:,1] , data[propeller][rpm][:,7] ,
                           linewidth = 0.9)
            
        a3.legend(ncol = 1 , loc = 'upper right' ,
                      fontsize = 6 , frameon = False)   
        fig.tight_layout()
        plt.show()
        return
    def get_data(self , propeller , RPM):
        datos = []
        for rpm in RPM:
            datos.append(['','','','RPM',str(rpm[4:]),'','',''])
            datos.append(['V','J','Pe','Ct','Cp','PWR','Torque','Thrust'])
            data = Propellers.database(self)[propeller][rpm]
            for line in data:
                datos.append(line)
        pd.DataFrame(np.asarray(datos)).to_csv('Data__' + propeller + '.csv' ,header = None , index = None)
        return
            
        
if __name__ == "__main__":
    """
    This line calls the main class Propeller and assigns it to the variable analysis
    """
    analysis = Propellers()
    """
    The following lines call the function propeller_selection . This function requires 3 inputs
    1.- flight speed , 2.- Thrust required , 3.- System of Units SI
    if SI = True  ===> inputs and results are expressed in the International System of Units
    if SI = False ===> inputs and results are expressed in the British System of Units
    """
    analysis.propeller_selection(50 , 8  , SI = False)
    analysis.propeller_selection(11 , 130 , SI = True)
    """
    This command print the list of all propellers in the database : 509
    """
    print(analysis.all_propellers())
    """
    This line calls the function info_propeller that returns the values of RPM
    (for which data is available) for a specific propeller
    input: Propeller name
    """
    print(analysis.info_propeller('Propeller_105x45'))
    """
    This line calls the function propeller_performance. This function returns a plot chart
    about performance characteristics for all RPM values, for a given propeller
    """
    analysis.performance_propeller('Propeller_105x45')
    """
    This line calls the function compare_propellers. This function returns a plot chart
    about performance characteristics for two or more propellers and for a given number of RPM.
    For this, all the propellers must have data for the given RPM values 
    """
    analysis.compare_propellers(['Propeller_9x6', 'Propeller_105x45'],
                                ['RPM 1000' ,
                                 'RPM 2000' ,
                                 'RPM 3000'])
    """
    This line calls the function get_data that returns the performance date for a given propeller
    and for a given range of propellers
    """
    analysis.get_data('Propeller_105x45', ['RPM 1000' , 'RPM 2000'])
    
    

       
        
    

    
