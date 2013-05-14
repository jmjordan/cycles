from __future__ import division
import sqlite3 as lite
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
import time
import sys
import os

def list_commands():
    print ""
    print "  Type 'new' to log a cycle."
    print "  Type 'list' to show all cycles."
    print "  Type 'stats' to show information on cycle history."
    print "  Type 'edit' to edit a cycles start date or period end date."
    print "  Type 'quit' to save and exit."

def display_menu():
    print ""
    print "  Type 'help' for a list of commands."
    return raw_input("> ")
    
# Returns a datetime based on an input
def ask_for_dt(question):
    now = datetime.today()
    date_str = raw_input("%s [%s]? "%(question,now.strftime('%b %d, %Y %H:%M')))
    if (date_str == ""):
        return now
    else:
        try:
            return parse(date_str)
        except Exception,e:
            print "That date is invalid: %s. Please try again."%e
            return ask_for_dt(question)

def new_cycle(con):
    new_start_date_str = ask_for_dt("When did the cycle start").strftime('%b %d, %Y %H:%M')
    if new_start_date_str == -1:
        return False
    if new_start_date_str != "":
        try:
            new_start_dt = int(parse(new_start_date_str).strftime("%s"))
            if new_start_dt > int(datetime.today().strftime("%s")):
                raise Exception('future date')
        except Exception,e:
            print "That date is invalid: %s. Please try again."%e
            new_cycle(con)
            return False
    else:
        new_start_dt = int(datetime.today().strftime("%s"))
    cur = con.cursor()
    cur.execute("INSERT into cycles(start_dt) VALUES(%d)"%(new_start_dt))
    return True
    
def edit(con):
    cur = con.cursor()
    cur.execute("SELECT id,start_dt,period_end_dt FROM cycles order by start_dt desc")
    rows = cur.fetchall()
    if len(rows) == 0:
        print "You must log a cycle before you can edit."
        return False
    print "|---------- Cycles ------------|"
    print "|  # | Start Date | Period End |"
    for i in range(len(rows)): 
        start_dt = datetime.fromtimestamp(rows[i][1])
        period_end_dt_str = "--"
        if rows[i][2] != None:
            period_end_dt = datetime.fromtimestamp(rows[i][2])
            period_end_dt_str = period_end_dt.strftime("%Y-%m-%d")
        print "| %2s | %10s | %10s |"%(i+1,start_dt.strftime("%Y-%m-%d"),period_end_dt_str)
    print "|---------------------------------|"
    cycle_idx = raw_input("Which cycle would you like to edit [1]? ")
    cycle_id = int(rows[0][0])
    if cycle_idx != "":
        cycle_idx = int(cycle_idx)
        cycle_id = rows[cycle_idx-1][0]
    else:
        cycle_idx = 1
    new_start_dt = datetime.fromtimestamp(rows[cycle_idx-1][1])
    if rows[cycle_idx-1][2] != None:
        new_last_day_of_period = datetime.fromtimestamp(rows[cycle_idx-1][2])
    else:
        new_last_day_of_period = None
    print "\nCurrent start date: %s"%new_start_dt.strftime("%Y-%m-%d")
    print "Current last day of period: %s"%(new_last_day_of_period.strftime("%Y-%m-%d") if new_last_day_of_period != None else "--")
    choice = raw_input("\n1) Edit start date\n2) Edit last day of period\n3) Delete this cycle\n> ")
    if choice == '1':
        new_start_dt = ask_for_dt("What date did the cycle start")
    elif choice == '2':
        new_last_day_of_period = ask_for_dt("What was the last day of the period starting on %s"%new_start_dt.strftime("%b %d, %Y"))
    elif choice == '3':
        delete_cycle(con,cycle_id)
        return True
    else:
        return False
    edit_cycle(con,cycle_id,new_start_dt,new_last_day_of_period)
    
    return True
    
def dt_to_ts(dt):
    if dt != None:
        return int(dt.strftime("%s"))
    else:
        return -1
        
def delete_cycle(con,cycle_id):
    cur=con.cursor()
    confirm = raw_input("Are you sure [Y/n]?")
    if confirm == "Y":
        cur.execute("DELETE FROM cycles WHERE id=%d"%cycle_id)
    elif confirm == "n":
        return
    else:
        return delete_cycle(con,cycle_id)

def edit_cycle(con,cycle_id,start_dt,last_day_of_period):
    cur = con.cursor()
    
    print "Update cycle %d... setting start_date to %s(%s) and last_day_of_period to %s(%s)."%(cycle_id,start_dt,dt_to_ts(start_dt),last_day_of_period if last_day_of_period != None else 'null',dt_to_ts(last_day_of_period) if last_day_of_period != None else 'null')
    if start_dt != None:
        cur.execute("UPDATE cycles set start_dt=%s where id=%s"%(dt_to_ts(start_dt),cycle_id))
    else:
        print "Cannot change start_date to blank!"
        
    if last_day_of_period == None:
        cur.execute("UPDATE cycles set period_end_dt=null where id=%s"%(cycle_id))
    else:
        cur.execute("UPDATE cycles set period_end_dt=%s where id=%s"%(dt_to_ts(last_day_of_period),cycle_id))
        
    return
    
def compute_period_length(start_dt,period_end_dt):
    if period_end_dt == None:
        return -1
    length = datetime.fromtimestamp(period_end_dt) - datetime.fromtimestamp(start_dt)
    return length.days + length.seconds/86400
    
def compute_cycle_length(previous_start_dt, start_dt):
    length = datetime.fromtimestamp(start_dt) - datetime.fromtimestamp(previous_start_dt)
    return length.days + length.seconds/86400
    
def last_n_cycles(con,n):
    cur = con.cursor()
    
    
    if n == 0:
        cur.execute("SELECT id,start_dt,period_end_dt FROM cycles order by start_dt desc")
        print "|------------ Cycles ------------|"
    else:
        cur.execute("SELECT id,start_dt,period_end_dt FROM cycles ORDER BY start_dt DESC LIMIT %d"%n)
        print "|--------- Last %d Cycles --------|"%n
    
    rows = cur.fetchall()    
    print "| Cycle        | Flow   | Cycle  |"
    print "| Start Date   | Length | Length |"
    print "|--------------------------------|"
    if len(rows) > 0:
        for i in range(len(rows)):
            length = -1
            if i > 0:
                length = compute_cycle_length(rows[i][1],rows[i-1][1])
            start_dt = datetime.fromtimestamp(rows[i][1])
            period_length = compute_period_length(rows[i][1],rows[i][2])
            print "| %10s | %6s | %6s |"%(start_dt.strftime("%b %d, %Y"),(round(period_length,1) if period_length != -1 else '--'),(round(length,1) if length != -1 else '--'))
    else:
        print "|        No cycles logged        |"
    print "|--------------------------------|"
    return True
    
def show_all(con):
    return last_n_cycles(con,0)
    
def stats(con):
    cur = con.cursor()
    cur.execute("SELECT start_dt,period_end_dt FROM cycles order by start_dt desc")
    rows = cur.fetchall()
    lengths_sum = 0
    period_lengths_sum = 0
    complete_cycle_count = 0
    valid_cycle_count = 0
    period_lengths_count = 0
    longest_cycle_length = 0
    longest_cycle_dt = None
    shortest_cycle_length = 0
    shortest_cycle_dt = None
    last_start_dt = None
    for i in range(len(rows)):
        period_length = compute_period_length(rows[i][0],rows[i][1])
        if i > 0:
            complete_cycle_count += 1
            cycle_length = compute_cycle_length(rows[i][0],rows[i-1][0])
            if cycle_length >= 21 and cycle_length <= 35:
                lengths_sum += cycle_length
                valid_cycle_count += 1
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
        average_length = lengths_sum/valid_cycle_count
        next_start_dt = last_start_dt + timedelta(days=average_length)
        if period_lengths_count > 0:
            average_period_length = period_lengths_sum/period_lengths_count
        days_till_next_cycle = (next_start_dt - datetime.today()).days
        print ""
        print "Currently in day %d of cycle."%((datetime.today() - last_start_dt).days+1)
        if days_till_next_cycle < 0:
            print "Next cycle is %s %s late. Should have started on %s."%(abs(days_till_next_cycle),"day" if days_till_next_cycle == 1 else "days",next_start_dt.strftime('%a, %b %d'))
        else:
           print "Next cycle starts in %d day(s) on %s."%((next_start_dt - datetime.today()).days,next_start_dt.strftime('%a, %b %d'))
        print ""
        print "Average cycle length.... %s days"%round(average_length,1)
        if period_lengths_count > 0:
            print "Average period length... %s days"%round(average_period_length,1)
        print "Cycles logged .......... %d"%complete_cycle_count
        print "Shortest cycle.......... %d days / %s - %s"%(shortest_cycle_length,shortest_cycle_dt.strftime('%b %d, %Y'),(shortest_cycle_dt + timedelta(days=shortest_cycle_length)).strftime('%b %d, %Y'))
        print "Longest cycle........... %d days / %s - %s"%(longest_cycle_length,longest_cycle_dt.strftime('%b %d, %Y'),(longest_cycle_dt + timedelta(days=longest_cycle_length)).strftime('%b %d, %Y'))
    else:
        print ""
        print "  Type 'new' to add a cycle."
    return True    
    

db_dir=os.path.expanduser('~/.cycles')
db_path=os.path.join(db_dir,'cycles.db')

con = None

if not os.path.exists(db_path):
    if not os.path.exists(db_dir):
        os.makedirs(db_dir) 
    print("[database created at {}]".format(db_path))
    open(db_path, 'a').close()
    con = lite.connect(db_path)
    cur = con.cursor()    
    cur.execute("CREATE TABLE cycles(id INTEGER PRIMARY KEY, start_dt INTEGER, period_end_dt INTEGER)")
else:
    con = lite.connect(db_path)

with con:  
    show_cycles_after_command = True  
    while 1:
        
        if show_cycles_after_command == True:
            last_n_cycles(con,4)
            stats(con)
        choice = display_menu()
        if choice == 'new':
            #Enter a new date
            new_cycle(con)
            show_cylces_after_command = True
        elif choice == 'list':
            show_all(con)
            show_cycles_after_command = False
        elif choice == 'stats':
            show_cycles_after_command = True
        elif choice == 'edit':
            edit(con)
            show_cylces_after_command = True
        elif choice == 'help':
            show_cycles_after_command = list_commands()
        elif choice == 'quit' or choice == 'exit':
            con.commit()
            sys.exit(0)
        else:
            show_cycles_after_command = False
        con.commit()
      

