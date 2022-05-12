#!/usr/bin/env python3

from collections import OrderedDict
from datetime import datetime
import sys
import os
from time import time

from peewee import *

db = SqliteDatabase('diary.db')

class Entry(Model):
    content = TextField() # using textfield instead of varchar b/c varchar require a maximum length
    timestamp = DateTimeField(default=datetime.now) # note, leaving out the parentheses after now ensures the correct datetime is added to db.. e.g. whenever item is created, and not whenever script is run which would give us one datetime for all entries
    
    class Meta:
        database = db

def initialize():
    """Create the database and the table if they don't exist."""
    db.connect()
    db.create_tables([Entry], safe=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear') # call cls if windows, call clear if on linux/mac

def menu_loop():
    """Show the menu"""
    choice = None # initialize our choice variable

    while choice != 'q':
        clear() # clear the screen
        print('Enter "q" to quit.')
        for key, value in menu.items():
            print(f'{key}) {value.__doc__}') # value is a function and the .__doc__ is the docstring for that function
        choice = input('Action: ').lower().strip() #lower case user input and strip off any extra spaces

        if choice in menu:
            clear() # clear screen
            menu[choice]()

def add_entry():
    """Add an entry"""
    print('Enter your entry. Press ctrl+d when finished.')
    data = sys.stdin.read().strip()

    if data:
        if input('Save entry? [Y/N] ').lower() != 'n':
            Entry.create(content=data)
            print('Saved successfully!')



def view_entries(search_query=None):
    """View previous entries."""
    entries = Entry.select().order_by(Entry.timestamp.desc()) # oldest one shows up last, e.g. newest first
    if search_query:
        entries = entries.where(Entry.content.contains(search_query)) # if user adds search_query, we filter for matching criteria

    for entry in entries:
        timestamp = entry.timestamp.strftime('%A %B %d, %Y %I:%M%p')
        clear() # clear screen
        print(timestamp)
        print('='*len(timestamp))
        print(entry.content)
        print('\n\n'+'='*len(timestamp))
        print('n) next entry')
        print('d) delete entry')
        print('q) return to main menu')

        next_action = input('Action: [N/d/q] ').lower().strip()
        if next_action == 'q':
            break
        elif next_action == 'd':
            delete_entry(entry)

def search_entries():
    """Search entries for a string."""
    view_entries(input('Search query: ')) #simple calline view_entries function but grabbing some user input first

def delete_entry(entry):
    """Delete an entry."""
    if input('Are you sure? [Y/N]').lower() == 'y':
        entry.delete_instance() # deletes the entry we are on if user enters y
        print('Entry deleted!')


# OrderedDict unlike a regular dictionary also remembers the order things are added
menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
    ('s', search_entries),
])

if __name__ == '__main__':
    initialize()
    menu_loop()