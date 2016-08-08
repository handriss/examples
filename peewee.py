""" Creating a new record """

# Creating a record with a single method call:
Model.create()
User.create(username="Charlie")
User.create(username="Mickey", age=23)

# Creating a record with multiple calls:
user = User(username="Charlie")
user.age = 24
user.save()

# If the created object has a foreign key, we can directly assign it to a model instance:
dog = Dog.create(owner=user, name="Spike")

# ... or we can assign it to the model instance's primary key:
dog = Dog.create(owner=1, name="Spike")

# If I do not want to create a model instance, I can also insert with:
Dog.insert(owner=1, name="Spike").execute()


""" Bulk inserts """

# The naive approach, which is quite slow:
data_source = [
    {'field1': 'val1-1', 'field2': 'val1-2'},
    {'field1': 'val2-1', 'field2': 'val2-2'},
    # ...
]

for data_dict in data_source:
    Model.create(**data_dict)

# Wrapping it into atomic() makes it much faster:
with db.atomic():
    for data_dict in data_source:
        Model.create(**data_dict)

# Fastest approach, if we give in a list of dictionaries:
with db.atomic():
    Model.insert_many(data_source).execute()

# I can break up insertions into chunks:
# Insert rows 100 at a time.
with db.atomic():
    for idx in range(0, len(data_source), 100):
        Model.insert_many(data_source[idx:idx+100]).execute()


# Creating a table based on another table:
query = (TweetArchive
         .insert_from(
             fields=[Tweet.user, Tweet.message],
             query=Tweet.select(Tweet.user, Tweet.message))
         .execute())


""" Updating existing records """

# If a model instance has a primary key, the save() method will update it

# Updating multiple records:
query = Person.update(has_birthday=True).where(Person.birthdate == today)
query.execute()

q = User.update(active=False).where(User.registration_expired == True)
q.execute()

# The same, using UpdateQuery class:
uq = UpdateQuery(User, active=False).where(User.registration_expired == True)
uq.execute()


""" Deleting """

# Deleting a given model instance:
planet = Planet.get(Planet.name == "Alderaan")
planet.delete_instance()

# Deleting any dependent objects:
planet.delete_instance(recursive=True)


# Deleting a number of records:
query = Planet.delete().where(Planet.owners == "rebels")
query.execute()


""" Selecting a single record """

# Select a single model instance, gives DoesNotExist exception if nothing is found:
Planet.get(Planet.id == 1)

# Selecting a single model instance with more advanced conditions:
Planet.select().join(Galaxy).where(Planet.mass > 9.0E+100).order_by(Galaxy.size.desc()).get()


""" Create or get """

# I want to create a new user account, but username is a unique field:
try:
    with db.atomic():
        return User.create(username=username)
except peewee.IntegrityError:
    # `username` is a unique column, so this username already exists,
    # making it safe to call .get().
    return User.get(User.username == username)

# I can call create_or_get() instead of all this long code (user is the model instance,
# created is a boolean whether the record was created):
user, created = User.create_or_get(username=username)

# If I want to get the instance first:
user, created = User.get_or_create(username=username)

# Getting a person based on first and last name, but if no person is found
# I give in her birth of date and favourite color as well:
person, created = Person.get_or_create(
    first_name=first_name,
    last_name=last_name,
    defaults={'dob': dob, 'favorite_color': 'green'})


""" Selecting multiple records """

# Iterating over all rows:
for planet in Planet.select():
    print(planet.name)

# If I have a foreignkey assigned to model, I can use related_name to create a back-reference:
# - Planet model has Planet.owner foreignkeyfield
# - empire and rebels model instances are owners of planets

# Accessing the given planets owner (there can be only one owner):
planet = Planet.get(Planet.name == "Alderaan")
print(planet.owner)

# Accessing all planets owned by a given faction:
owner = Owner.get(Owner.name == "Galactic Empire")
owner.planets # it return a query, through which I can iterate
for planet in owner.planets:
    print(planet.name)


""" Filtering queries """

# For a singl record with get:
planet = Planet.get(Planet.name == "Alderaan")

# For multple records with select use where:
query = Planet.delete().where(Planet.owners == "rebels")

# There are multiple query operators, two notable operators:
<< # in operator, searching in a query or list
>> None # None/Null operators

# I can use python's AND and OR operators:
Planet.select().where(
    (Planet.has_atmosphere == True) &
    (Planet.is_terrestrial == True)
)

# Get tweets by staff or superusers (assumes FK relationship):
Tweet.select().join(User).where(
    (User.is_staff == True) | (User.is_superuser == True))

# Get tweets by staff or superusers using a subquery:
staff_super = User.select(User.id).where(
    (User.is_staff == True) | (User.is_superuser == True))
Tweet.select().where(Tweet.user << staff_super)


""" Sorting records """

# Returning rows in ascending order:
Planet.select().order_by(Planet.mass)

Planet.select().order_by(Planet.mass.asc())

Planet.select().order_by(+Planet.mass)

# Returning records in descending order:
Planet.select().order_by(Planet.mass.desc()):

Planet.select().order_by(-Planet.mass)

# Ordering by multiple values, first by name of her capital city then by mass:
Planet.select().order_by(Planet.capital_city, Planet.mass)

# Ordering based on count:
query = (User
         .select(User.username, fn.COUNT(Tweet.id).alias('num_tweets'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User.username)
         .order_by(fn.COUNT(Tweet.id).desc()))

# Ordering based on count using SQL in order_by:
query = (User
         .select(User.username, fn.COUNT(Tweet.id).alias('num_tweets'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User.username)
         .order_by(SQL('num_tweets').desc()))


""" Getting random records """
LotteryNumber.select().order_by(fn.Random()).limit(5)

""" Paginating records """
Tweet.select().order_by(Tweet.id).paginate(2, 10)

""" Counting records """
Tweet.select().count()
Tweet.select().where(Tweet.id > 50).count()


""" Aggregating records """

# Get usernames and the number of tweets created by them:
query = User.select().annotate(Tweet)

query = (User
         .select(User, fn.Count(Tweet.id).alias('count'))
         .join(Tweet)
         .group_by(User))

# Include users with 0 tweets use left join:
query = (User
         .select()
         .join(Tweet, JOIN.LEFT_OUTER)
         .switch(User)
         .annotate(Tweet))

""" Retrieving scalar values """

# Return a single scalar value:
PageView.select(fn.Count(fn.Distinct(PageView.url))).scalar()

# Return a tuple of scalar values:
Employee.select(
    fn.Min(Employee.salary), fn.Max(Employee.salary)
).scalar(as_tuple=True)
