import sqlite3 as lite
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
import time
import sys
import os

def list_commands():
    print "  Type 'new' to log a cycle."
    print "  Type 'edit' to edit a cycles start date or period end date."
    print "  Type 'quit' to save and exit."

def display_menu():
    print ""
    print "  Type 'help' for a list of commands."
    return raw_input("> ")
    
# Returns a datetime based on an input
def ask_for_dt(question):
    date_str = raw_input("%s [%s]? "%(question,datetime.today().strftime('%b %d, %Y')))
    if (date_str == ""):
        return parse(datetime.today().strftime('%b %d, %Y'))
    else:
        return parse(date_str)
    
def new_cycle(con):
    new_start_date_str = raw_input("When did the cycle start [%s]? "%(datetime.today().strftime('%b %d, %Y')))
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
    print "|------------- Cycles ------------|"
    print "| Cycle | Start Date | Period End |"
    for i in range(len(rows)): 
        start_dt = datetime.fromtimestamp(rows[i][1])
        period_end_dt_str = "--"
        if rows[i][2] != None:
            period_end_dt = datetime.fromtimestamp(rows[i][2])
            period_end_dt_str = period_end_dt.strftime("%Y-%m-%d")
        print "| %5s | %10s | %10s |"%(i+1,start_dt.strftime("%Y-%m-%d"),period_end_dt_str)
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
    choice = raw_input("\n1) Edit start date\n2) Edit last day of period\n> ")
    if choice == '1':
        new_start_dt = ask_for_dt("What date did the cycle start")
    elif choice == '2':
        new_last_day_of_period = ask_for_dt("What was the last day of the period starting on %s"%new_start_dt.strftime("%b %d, %Y"))
    else:
        return
    edit_cycle(con,cycle_id,new_start_dt,new_last_day_of_period)
    
    return True
    
def dt_to_ts(dt):
    if dt != None:
        return int(dt.strftime("%s"))
    else:
        return -1

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
    return (datetime.fromtimestamp(period_end_dt) - datetime.fromtimestamp(start_dt)).days
    
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
    if len(rows) > 0:
        for i in range(len(rows)):
            length = -1
            if i > 0:
                length = compute_cycle_length(rows[i][1],rows[i-1][1])
            start_dt = datetime.fromtimestamp(rows[i][1])
            period_length = compute_period_length(rows[i][1],rows[i][2])
            print "| %10s | %6s | %6s |"%(start_dt.strftime("%b %d, %Y"),(period_length if period_length != -1 else '--'),(length if length != -1 else '--'))
    else:
        print "|        No cycles logged        |"
    print "|--------------------------------|"
    return True
    
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
            if cycle_length >= 21 and cycle_length <= 35:
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
        days_till_next_cycle = (next_start_dt - datetime.today()).days
        print ""
        print "Currently in day %d of cycle."%((datetime.today() - last_start_dt).days+1)
        if days_till_next_cycle < 0:
            print "Next cycle is %s %s late. Should have started on %s."%(abs(days_till_next_cycle),"day" if days_till_next_cycle == 1 else "days",next_start_dt.strftime('%a, %b %d'))
        else:
           print "Next cycle starts in %d day(s) on %s."%((next_start_dt - datetime.today()).days,next_start_dt.strftime('%a, %b %d'))
        print ""
        print "Average cycle length.... %d days"%average_length
        if period_lengths_count > 0:
            print "Average period length... %d days"%average_period_length
        print "Cycles logged .......... %d"%complete_cycle_count
        print "Shortest cycle.......... %d days / %s - %s"%(shortest_cycle_length,shortest_cycle_dt.strftime('%b %d, %Y'),(shortest_cycle_dt + timedelta(days=shortest_cycle_length)).strftime('%b %d, %Y'))
        print "Longest cycle........... %d days / %s - %s"%(longest_cycle_length,longest_cycle_dt.strftime('%b %d, %Y'),(longest_cycle_dt + timedelta(days=longest_cycle_length)).strftime('%b %d, %Y'))
    else:
        print ""
        print "  Type 'new' to add a cycle."
    return True    
    

db_dir=os.path.dirname(os.path.realpath(__file__))
db_path=os.path.join(db_dir,'cycles.db')

con = None

if not os.path.exists(db_path):
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
        
        if show_cycles_after_command:
            os.system('clear')
            print ""
            show_all(con)
            stats(con)
        choice = display_menu()
        if choice == 'new':
            #Enter a new date
            new_cycle(con)
            show_cylces_after_command = True
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
      

