from dataclasses import dataclass
from datetime import datetime
from email.policy import default

from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE =  SqliteDatabase('social.db')

class User(UserMixin, Model): #mixins are like chocolate chips, we put them before our main parent class Model
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.now)
    is_admin = BooleanField(default=False)


    class Meta:
        database = DATABASE
        order_by = ('-joined_at',) # list all users, ordered by joined at descending

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )

    @classmethod #a method that belongs to a class, that can create the class it belongs to 
    def create_user(cls, username, email, password, admin=False): # with cls, it will create the user model instance when it runs this method and use it in the create
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin
            )
        except IntegrityError: # thrown if username or email are not actually unique
            raise ValueError('User already exists') # raise a value error


class Post(Model):
    timestamp = DateTimeField(default=datetime.now)
    user = ForeignKeyField(
        rel_model=User, #model that this foreign key points to, e.g. User model
        related_name='posts', #what the related model would call this model... if you're a user, what do you call the post model you created.. 'posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',) #display newest items first, because those items are tuples, we need to make sure we include the comma

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()
