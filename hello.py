from random import seed
from random import randint

seed(1)

hello = ['Hi there!', 'Hello!', 'Have a good day!', 'Tada!']

def sayHello():
    return hello[randint(0, 3)]