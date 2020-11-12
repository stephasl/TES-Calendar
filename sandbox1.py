#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 19:30:52 2020

@author: Steve
"""


# ask for overtime:
x= input('Any Overtime? (Y or N)')
if x[0] in ['Y', 'y']:
        while True:
            which_day = int(input('On what day?')) #need to put an error trap on this
            print(workwith.iloc[(which_day * 2 -2):(which_day * 2),0:4])
            how_much = float(input('How many hours (as a decimal)'))
            dn = input('Which shift? Day or Night (d/n)')
            if dn[0] in ['D','d','N','n']:
                if dn[0] in ['D','d']:
                    dummy_col[(which_day * 2 -1)]= how_much
                else:
                    dummy_col[(which_day * 2 )]= how_much
                x= input('another? (y/n)')
                if x[0] in ['Y', 'y']:
                    continue
                else: 
                    break
           
            else:
                restart = input("Sorry, didn't catch that, try again? (y/n)")
                if restart[0] in ['Y', 'y']:
                    continue
                else:
                    break