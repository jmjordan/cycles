cycles
======

A command line utility for logging menstrual cycles.

*cycles* provides an easy to use way to keep track of your past, present, and future cycles.

### In a nutshell

To install *cycles* enter the following:

	git clone https://github.com/jmjordan/cycles.git
	cd cycles
	sudo python setup.py install

To launch, *cycles* type `cycles` and hit return. The first time you do this it will create a database at `~/.cycles/cycles.db`

This is what the *cycles* interface looks like when first launched:

    [database created at /Users/<username>/.cycles/cycles.db]
    |--------- Last 4 Cycles --------|
    | Cycle        | Flow   | Cycle  |
    | Start Date   | Length | Length |
    |--------------------------------|
    |        No cycles logged        |
    |--------------------------------|
    
	    Type 'new' to add a cycle.
    
	    Type 'help' for a list of commands.
    > 

Type `new` to log the start of a cycle.

Once more than one cycle has been logged, *cycles* will show statistics for your cycle history and will give an estimate for when your next cycle might begin.

Type `quit` to exit *cycles*.

#### Adding

To log the start of a menstrual cycles type `new` and hit return.

Enter the day the cycle started (it defaults to the current date/time) and hit enter.

Once you have enter more than one cycle, *cycles* will give you statistics on your menstrual cycle history and provide an estimated date for the start of your next cycle.

    |--------- Last 4 Cycles --------|
    | Cycle        | Flow   | Cycle  |
    | Start Date   | Length | Length |
    |--------------------------------|
    | Apr 28, 2013 |    5.0 |     -- |
    | Apr 01, 2013 |    6.0 |   27.0 |
    | Mar 06, 2013 |    7.0 |   26.0 |
    | Feb 07, 2013 |    6.0 |   27.0 |
    |--------------------------------|
    
    Currently in day 16 of cycle.
    Next cycle starts in 10 day(s) on Fri, May 24.
    
    Average cycle length.... 26.0 days
    Average period length... 5.8 days
    Cycles logged .......... 4
    Shortest cycle.......... 24 days / Jan 14, 2013 - Feb 07, 2013
    Longest cycle........... 27 days / Apr 01, 2013 - Apr 28, 2013

#### Viewing

To view a list of every cycle that has been logged, enter `list` and hit enter.

    |------------ Cycles ------------|
    | Cycle        | Flow   | Cycle  |
    | Start Date   | Length | Length |
    |--------------------------------|
    | Apr 28, 2013 |    5.0 |     -- |
    | Apr 01, 2013 |    6.0 |   27.0 |
    | Mar 06, 2013 |    7.0 |   26.0 |
    | Feb 07, 2013 |    6.0 |   27.0 |
    | Jan 14, 2013 |    5.0 |   24.0 |
    |--------------------------------|    

#### Editing/Deleting

To edit or delete an entry type `edit` and hit enter.

This will show a list of all cycles starting with most recent:

    |---------- Cycles ------------|
    |  # | Start Date | Period End |
    |  1 | 2013-04-28 | 2013-05-03 |
    |  2 | 2013-04-01 | 2013-04-07 |
    |  3 | 2013-03-06 | 2013-03-13 |
    |  4 | 2013-02-07 | 2013-02-13 |
    |  5 | 2013-01-14 | 2013-01-19 |
    |---------------------------------|
    Which cycle would you like to edit [1]? 

Enter the number of the cycle you would like to edit and hit enter. You will now be asked what you would like to do:
    
    1) Edit start date
    2) Edit last day of period
    3) Delete this cycle

Enter your choice and hit enter.

Enter the new date or confirm if you would like to delete the cycle and hit enter.

#### Commands

* `new` - log the start of a cycle
* `list` -  show all cycles
* `stats` - show information on cycle history
* `edit` - edit a cycle's start date or period end date
* `quit` - exit *cycles*

