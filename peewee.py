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
