from enum import unique
from peewee import *

db = SqliteDatabase('students.db')

class Student(Model): # represents a single item in a database theoretically
    username = CharField(max_length=255, unique=True) # if username is not provided, produces error b/c no default 
    points = IntegerField(default=0)

    class Meta: # tell model what database it belongs to
        database = db


students = [
    {'username': 'khaledadad',
    'points': 4888},
    {'username': 'chalkers',
    'points': 11912},
    {'username': 'joykesten2',
    'points': 7363},
    {'username': 'craigsdenni',
    'points': 4079},
    {'username': 'davemcfarland',
    'points': 14717},
]

def add_students():
    for student in students:
        try:
            Student.create(username=student['username'], points=student['points'])
        except IntegrityError:
            student_record = Student.get(username=student['username'])
            student_record.points = student['points'] # if the record already exists, update the points
            student_record.save()

def top_student():
    student = Student.select().order_by(Student.points.desc()).get() # .get() only grabs the first record to come back         
    return student.username

if __name__ == '__main__': # if file is run directly and not imported
    db.connect() # connect to database
    db.create_tables([Student], safe=True) # if ran multiple times
    add_students()
    print(f'Our top student right now is: {top_student()}')