#!/usr/bin/env python

import random


""" Checking random.choice() for randomness """

the_list = [1, 2, 3]

random_picks = []

for i in range(100):
    random_picks.append(random.choice(the_list))

print(f"No. of 1s: {random_picks.count(1)}")
print(f"No. of 2s: {random_picks.count(2)}")
print(f"No. of 3s: {random_picks.count(3)}")
