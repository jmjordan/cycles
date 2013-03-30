import sqlite3 as lite
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
import time
import sys
from os import path,system

def display_menu():
    return raw_input("> ")
    
def new_cycle(con):
    new_start_date_str = raw_input("When did this cycle start [%s]? "%(datetime.today().strftime('%b %d, %Y')))
    if new_start_date_str != "":
        try:
            new_start_dt = int(parse(new_start_date_str,default=datetime.today()).strftime("%s"))
            if new_start_dt > int(datetime.today().date().strftime("%s")):
                raise Exception('future date')
        except Exception,e:
            print "That date is invalid: %s. Please try again."%e
            new_cycle(con)
            return
    else:
        new_start_dt = int(datetime.today().strftime("%s"))
    cur = con.cursor()
    cur.execute("INSERT into cycles(start_dt) VALUES(%d)"%(new_start_dt))
    return
    
def edit(con):
    cur = con.cursor()
    cur.execute("SELECT * FROM cycles order by id desc")
    rows = cur.fetchall()
    print "|------------- Cycles ------------|"
    print "| Cycle | Start Date | Period End |"
    for i in range(len(rows)):
        length = rows[i][2]  
        start_date = datetime.strptime(rows[i][1],"%Y-%m-%d").date()
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
    
def compute_period_length(start_dt,period_end_dt):
    if period_end_dt == None:
        return -1
    return (datetime.fromtimestamp(period_end_dt) - datetime.fromtimestamp(start_dt)).days + 1
    
def compute_cycle_length(previous_start_dt, start_dt):
    return (datetime.fromtimestamp(start_dt) - datetime.fromtimestamp(previous_start_dt)).days
    

    
def show_all(con):
    cur = con.cursor()
    cur.execute("SELECT id,start_dt,period_end_dt FROM cycles order by start_dt desc")
    rows = cur.fetchall()
    print "|------------ Cycles ------------|"
    print "| Cycle        | Flow   | Cycle  |"
    print "| Start Date   | Length | Length |"
    print "|--------------------------------|"
    for i in range(len(rows)):
        length = -1
        if i > 0:
            length = compute_cycle_length(rows[i][1],rows[i-1][1])
        start_dt = datetime.fromtimestamp(rows[i][1])
        period_length = compute_period_length(rows[i][1],rows[i][2])
        print "| %10s | %6s | %6s |"%(start_dt.strftime("%b %d, %Y"),(period_length if period_length != -1 else '--'),(length if length != -1 else '--'))
    print "|--------------------------------|"
    return
    
def stats(con):
    cur = con.cursor()
    cur.execute("SELECT start_dt,period_end_dt FROM cycles order by start_dt desc")
    rows = cur.fetchall()
    lengths_sum = 0
    period_lengths_sum = 0
    complete_cycle_count = 0
    period_lengths_count = 0
    longest_cycle_length = 0
    longest_cycle_dt = None
    shortest_cycle_length = 0
    shortest_cycle_dt = None
    last_start_dt = None
    for i in range(len(rows)):
        period_length = compute_period_length(rows[i][0],rows[i][1])
        if i > 0:
            cycle_length = compute_cycle_length(rows[i][0],rows[i-1][0])
            lengths_sum += cycle_length
            complete_cycle_count += 1
            if (longest_cycle_dt == None) or (cycle_length > longest_cycle_length):
                longest_cycle_length = cycle_length
                longest_cycle_dt = datetime.fromtimestamp(rows[i][0])
            if (shortest_cycle_dt == None) or (cycle_length < shortest_cycle_length):
                shortest_cycle_length = cycle_length
                shortest_cycle_dt = datetime.fromtimestamp(rows[i][0])
        if period_length != -1:
            period_lengths_sum += period_length
            period_lengths_count += 1
        if i == (0):
            last_start_dt = datetime.fromtimestamp(rows[i][0])
    if complete_cycle_count > 0:
        average_length = lengths_sum/complete_cycle_count
        next_start_dt = last_start_dt + timedelta(days=average_length)
        if period_lengths_count > 0:
            average_period_length = period_lengths_sum/period_lengths_count
        print ""
        print "Currently in day %d of cycle."%((datetime.today() - last_start_dt).days+1)
        print "Next cycle starts in %d days on %s."%((next_start_dt - datetime.today()).days,next_start_dt.strftime('%a, %b %d'))
        print ""
        print "Average cycle length.... %d days"%average_length
        if period_lengths_count > 0:
            print "Average period length... %d days"%average_period_length
        print "Cycles tracked.......... %d"%complete_cycle_count
        print "Shortest cycle.......... %s / %d days"%(shortest_cycle_dt.strftime('%b %d, %Y'),shortest_cycle_length)
        print "Longest cycle........... %s / %d days"%(longest_cycle_dt.strftime('%b %d, %Y'),longest_cycle_length)
    else:
        print "No cycles entered"
    return     

db_path=path.join(path.dirname(path.realpath(__file__)),'cycles.db')
con = lite.connect(db_path)

with con:    
    while 1:
        system('clear')
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
      

