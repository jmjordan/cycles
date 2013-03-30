import sqlite3 as lite
from datetime import date
import datetime
import time
import sys
import os

def display_menu():
    return raw_input("> ")
    
def new_cycle(con):
    new_start_date_str = raw_input("When did this cycle start [%s]? "%(date.today().strftime('%Y-%m-%d')))
    cur = con.cursor()
    cur.execute("SELECT * FROM cycles order by id desc")
    row = cur.fetchone()
    if row != None:
        prev_id = row[0]
        start_date = datetime.datetime.strptime(row[1],"%Y-%m-%d").date()
        
        if new_start_date_str != "":
            new_start_date = datetime.datetime.strptime(new_start_date_str,"%Y-%m-%d").date()
        else:
            new_start_date_str = date.today().strftime('%Y-%m-%d')
            new_start_date = date.today()
        length = (new_start_date - start_date).days
        if length > 0:
            cur.execute("UPDATE cycles SET length=%d where id=%d"%(length,prev_id))
            cur.execute("INSERT into cycles(start_date,length) VALUES('%s',%d)"%(new_start_date_str,-1))
    else:
        cur.execute("INSERT into cycles(start_date,length) VALUES('%s',%d)"%(new_start_date_str,-1))
    return
    
def edit(con):
    cur = con.cursor()
    cur.execute("SELECT * FROM cycles order by id desc")
    rows = cur.fetchall()
    print "|------------- Cycles ------------|"
    print "| Cycle | Start Date | Period End |"
    for i in range(len(rows)):
        length = rows[i][2]  
        start_date = datetime.datetime.strptime(rows[i][1],"%Y-%m-%d").date()
        period_length = compute_period_length(rows[i][1],rows[i][3])
        print "| %5s | %10s | %10s |"%(i+1,rows[i][1],rows[i][3])
    print "|---------------------------------|"
    cycle = raw_input("Which cycle would you like to edit [1]? ")
    cycle_id = int(rows[0][0])
    if cycle != "":
        cycle = int(cycle)
        cycle_id = rows[cycle-1][0]
    else:
        cycle = 1
    new_start_date_str=rows[cycle-1][1]
    new_last_day_of_period_str=rows[cycle-1][3]
    print "Current start date: %s"%new_start_date_str
    print "Current last day of period: %s"%new_last_day_of_period_str
    choice = raw_input("\n1) Edit start date\n2) Edit last day of period\n> ")
    if choice == '1':
        new_start_date_str = raw_input("What is the new start date [YYYY-MM-DD]? ")
    elif choice == '2':
        new_last_day_of_period_str = raw_input("What is the new last day of period [YYYY-MM-DD]? ")
    else:
        return
    edit_cycle(con,cycle_id,new_start_date_str,new_last_day_of_period_str)
    
    return

def edit_cycle(con,cycle_id,start_date,last_day_of_period):
    cur = con.cursor()
    print "Update cycle %d... setting start_date to %s and last_day_of_period to %s."%(cycle_id,start_date,last_day_of_period if last_day_of_period != '' else 'null')
    if start_date != "":
        cur.execute("UPDATE cycles set start_date='%s' where id=%s"%(start_date,cycle_id))
    else:
        print "Cannot change start_date to blank!"
        
    if last_day_of_period == None or last_day_of_period == '':
        cur.execute("UPDATE cycles set last_day_of_period=null where id=%s"%(cycle_id))
    else:
        cur.execute("UPDATE cycles set last_day_of_period='%s' where id=%s"%(last_day_of_period,cycle_id))
        
#    cur.execute("UPDATE cycles set start_date='%s',last_day_of_period='%s' where id=%s"%(start_date,last_day_of_period if last_day_of_period != '' else 'null',cycle_id))
    return
    
def compute_period_length(start_date,last_day_of_period):
    if last_day_of_period == None:
        return -1
    return (datetime.datetime.strptime(last_day_of_period,"%Y-%m-%d").date() - datetime.datetime.strptime(start_date,"%Y-%m-%d").date()).days + 1
    

    
def show_all(con):
    cur = con.cursor()
    cur.execute("SELECT * FROM cycles")
    rows = cur.fetchall()
    print "|----------- Cycles -----------|"
    print "|            | Flow   | Cycle  |"
    print "| Start Date | Length | Length |"
    print "|------------------------------|"
    for i in range(len(rows)):
        length = rows[i][2]  
        start_date = datetime.datetime.strptime(rows[i][1],"%Y-%m-%d").date()
        period_length = compute_period_length(rows[i][1],rows[i][3])
        print "| %10s | %6s | %6s |"%(rows[i][1],(period_length if period_length != -1 else ''),(length if length != -1 else ''))
    print "|------------------------------|"
    return
    
def stats(con):
    cur = con.cursor()
    cur.execute("SELECT * FROM cycles")
    rows = cur.fetchall()
    lengths_sum = 0
    period_lengths_sum = 0
    count = 0
    period_lengths_count = 0
    longest_cycle = 0
    shortest_cycle = 99
    last_cycle_date = None
    for i in range(len(rows)):
        period_length = compute_period_length(rows[i][1],rows[i][3])
        if rows[i][2] != -1:
            lengths_sum += rows[i][2]
            count += 1
            if rows[i][2] > longest_cycle:
                longest_cycle = rows[i][2]
            if rows[i][2] < shortest_cycle:
                shortest_cycle = rows[i][2]
        if period_length != -1:
            period_lengths_sum += period_length
            period_lengths_count += 1
        if i == (len(rows)-1):
            last_cycle_date = datetime.datetime.strptime(rows[i][1],"%Y-%m-%d").date()
    if count > 0:
        average_length = lengths_sum/count
        next_cycle_date = last_cycle_date + datetime.timedelta(days=average_length)
        if period_lengths_count > 0:
            average_period_length = period_lengths_sum/period_lengths_count
        print ""
        print "Next cycle starts in %d days on %s."%((next_cycle_date - date.today()).days,next_cycle_date.strftime('%a, %b %d'))
        print "Currently in day %d of cycle."%((date.today() - last_cycle_date).days+1)
        print ""
        print "Average cycle length.... %d days"%average_length
        if period_lengths_count > 0:
            print "Average period length... %d days"%average_period_length
        print "Cycles tracked.......... %d"%count
        print "Shortest cycle.......... %d days"%shortest_cycle
        print "Longest cycle........... %d days"%longest_cycle
    else:
        print "No cycles entered"
    return     

con = lite.connect('/Users/jonathan/Dropbox/Scripts/cycles.db')

with con:    
    while 1:
        os.system('clear')
        show_all(con)
        stats(con)
        choice = display_menu()
        if choice == 'new':
            #Enter a new date
            new_cycle(con)
        elif choice == 'edit':
            edit(con)
        elif choice == 'quit':
            con.commit()
            sys.exit(0)
      

