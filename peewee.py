""" Querying """

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
