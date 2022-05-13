from datetime import datetime
from operator import index

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

    def following(self):
        """The users we are following."""
        return (
            User.select().join( # select all the users 
                Relationship, on=Relationship.to_user  # all the to_user's...
                # ^model .... ^key we're joining on
            ).where(
                Relationship.from_user == self # ...where the relationship is me
            )#^filter for: WHERE user = ME
        )

    def followers(self):
        """Get users following the current user."""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self # reverse of following
            )
        )

    @classmethod #a method that belongs to a class, that can create the class it belongs to 
    def create_user(cls, username, email, password, admin=False): # with cls, it will create the user model instance when it runs this method and use it in the create
        try:
            with DATABASE.transaction(): #transaction says, try this thing out, if it works, keep going, if it doesn't work, remove whatever action you just did -prevent getting locked out from Database
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
        # rel_model= User ... for some reason this isn't working, I just use User below and it runs
        User, #model that this foreign key points to, e.g. User model
        related_name='posts' #what the related model would call this model... if you're a user, what do you call the post model you created.. 'posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',) #display newest items first, because those items are tuples, we need to make sure we include the comma

class Relationship(Model):
    from_user = ForeignKeyField(User, related_name=('relationships'))#who are the people related to me
    to_user = ForeignKeyField(User, related_name=('related_to'))#who are the people I'm related to

    class Meta:
        database = DATABASE
        index = ( #allows us to specify how to find data as well as define a unique index, each index is a tuple
            (('from_user', 'to_user'), True) #true states that UNIQUE is required
        )

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
