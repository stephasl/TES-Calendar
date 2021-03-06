#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:44:31 2020

@author: Steve
"""
import numpy as np
import pandas as pd


parttimers  = []
partners    = ['J Cox','J Janzen','G Faller','S Rohrback','S Stephanides']
knownexcludes = []
newnames = []
days_in_mo ={  1:31, 2:28, 3:31,
               4:30, 5:31, 6:30,
               7:31, 8:31, 9:30,
              10:31,11:30,12:31}

debug = 1

### READ Part Timers data and Known deletes:
with open('parttimers.txt', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        nextpartimer = line[:-1]
        parttimers.append(nextpartimer)
#    close('parttimers.txt')
        
with open('known_excludes.txt', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        nextexclude = line[:-1]
        knownexcludes.append(nextexclude)       


rates = { 'D' :50, 'E': 75, 'H': 100}

"""
initial function definitions:
"""

def part_shift_list(df):  # assumes there is a field name in df
    for i in partners:
        print('shifts for: ', i) 
        if df[df.name ==i].empty:
            print("no shifts for ", i)
        else: 
            print(df[df.name == i])
            


def look_for_new_docs(df,partners,parttimers):  #expects a dataframe with a column 'name' and a list of names
    #look for new names or events that aren't a shift
    newnames = []
    for i in df.name:
        if i not in (partners + parttimers):  # sum is an appended list of all working docs
            if i not in newnames:    
                newnames.append(i)
    return newnames
        #CHRIS: I changed this function.  But I've got a cleaned dataset.  Is there a quick way to debug it?

def process_new(new_names):
    new_exclude=[]
    new_PT = []
    if new_names == None:
        return new_exclude, new_PT  # CHRIS: can I do this without repeating the return statement?  (eg. in a cleaner single loop?)
    else:
        print('for each name, please indicate if it is a P (part timer) or X (exclude)')
        for i in new_names:
            print(i);
            while True:
                x= input('P (part timer) or X (exclude)')
                if x in ['P', 'p']:
                    new_PT.append(i)
                    break
                elif x in ['X', 'x']:  
                    new_exclude.append(i)
                    break
                else:
                    print("Sorry, didn't catch that")
        return new_exclude, new_PT
            

def dn_to_text(num):    # should convert 12 to d and -23 to n
    if   num == 12.0:
        return 'd'
    elif num == -23.0:
        return 'n'
    else: 
        return 'err'
    
def shift_type(date,dn):  # expects a timestamp for date
    # will reteurn D for weekDAY E for WeekEND H for Holiday
    
    # redefine to work on panda series 
    date_aslist=date.tolist()
    dn_aslist  =dn.tolist()
    outlist = np.ones_like(dn_aslist)
    day_no =list(map(lambda f: f.weekday(),date_aslist))
    for i in range(len( day_no)):
        if day_no[i] < 4:
            outlist[i] = 'D'
        elif dn_aslist[i] == 'd':
            if day_no[i] == 4: outlist[i] =  'D'
            if day_no[i] == 5: outlist[i] =  'H'
            if day_no[i] == 6: outlist[i] =  'E'
        else:
            outlist[i] =  'E'
    return outlist

def shift_pay(shift,ot):   #expects (shift): in [D,H,E], (ot) : float num of hours
    return ( (12+ot)* rates[shift])

def remove_excludes(workwith,knownexcludes):
    for i in knownexcludes:
        workwith = workwith[workwith.name != i]
    return workwith
    #CHRIS: There's got to be a more efficient way to code this?
    
    
def append_file_lines(file_name, lines_to_append):
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        appendEOL = False
        # Move read cursor to the start of file.
        file_object.seek(0)
        # Check if file is not empty
        data = file_object.read(100)
        if len(data) > 0:
            appendEOL = True
        # Iterate over each string in the list
        for line in lines_to_append:
            # If file is not empty then append '\n' before first line for
            # other lines always append '\n' before appending line
            if appendEOL == True:
                file_object.write("\n")
            else:
                appendEOL = True
            # Append element at the end of file
            file_object.write(line)   


    
"""
main block
"""



# initial import of the big mess to df
# parse df down to workwith and change column names to less unwieldy

df = pd.read_csv('cal_data_spyder.csv',parse_dates=['Event Start','Event End'])

workwith =df[['Event Title','Event Start','Calculated Duration']]
workwith.columns =['name','date','dn']

# first draft at cleaning up file (get rid of known meetings and such)
workwith = remove_excludes(workwith,knownexcludes)

#get the set of rows which aren't in our known lists
# Which we downloaded in lines 23-35 (code starts with:)
#       with open('parttimers.txt', 'r') as filehandle: 
new_names = look_for_new_docs(workwith,partners,parttimers)

# Get user to divvy these into excludes or PT
new_excludes, new_PTdocs = process_new(new_names)

# get rid of the new excludes:
workwith = remove_excludes(workwith, new_excludes)

# now lets save that work to the TXT files so we don't have to redo it next month.
append_file_lines('known_excludes.txt', new_excludes) #save new exclude to file
append_file_lines('parttimers.txt'    , new_PTdocs)   #save new doc names to file

knownexcludes += new_excludes  # not sure if I use these again, might be able to delete
parttimers    += new_PTdocs


#check that we're working across one month:
    #is the month of first and last date entry the same? 
if workwith.date[0].month != workwith.date[workwith.index[-1]].month:
    print("It looks like you're working across more than one month")
    
tot_shifts = workwith.shape[0] # how many rows
this_month = workwith.date[0].month #what month is it (month number from datestamp)
                                    #we'll then use the dictionary to look it up
shift_deficit = 2* days_in_mo[this_month] - tot_shifts  
    #checking if there are 2 shifts/day this month
if  shift_deficit == 0 :
    print('Number of shifts seems right for month')
elif this_month ==2 and tot_shifts == 58:
    print('looks like it might be a leap year?')
elif shift_deficit > 0:
    print(f"you're short {shift_deficit} shifts")
else:
    print(f"Looks like {-shift_deficit} too many shifts")
    
dummy_col = np.zeros(tot_shifts)

    
# after that comes an error check:
    
    # TODO : ask for overtime
    # list of docs working? 
        #for i in PT, if i not in ww.name, print (i, " has no shifts")
    # TO DO: check for holidays
        # list all 'Type' == H, ask for others


# insert something here that looks for shifts that aren't d or n in dn2
        # should already be gone from the earlier thing...but might be better
        #to put this check first and clean out a lot of the meetings.
        # this would require moving line 104 up


#workwith['dn2']=workwith['dn']
workwith['dn']= workwith['dn'].apply((lambda row: dn_to_text(row)))
        #CHRIS:
        # these were failed attempts to do what the next line does and I'm
        #hoping they might help you explain what I'm not getting in this mess..

#workwith['dn2'] = workwith['dn'].map(dn_to_text)
                #creates a new column that elementwise maps the dn2text fn onto 'dn'
                #CHRIS:
                #this works but throws an error SettingWithCopyWarning
                
workwith['type']= shift_type(workwith.date,workwith.dn)

workwith['Overtime'] = dummy_col

# do I 

