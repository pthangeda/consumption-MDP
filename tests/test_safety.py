#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fimdp import consMDP
from math import inf
from fimdp.energy_solver import BasicES, LeastFixpointES
from sys import stderr

# ## Simple example

m = consMDP.ConsMDP()
m.new_states(13)
for sid in [0,3,4,9,11]:
    m.set_reload(sid)

# +
m.add_action(1, {0:.5, 2: .25, 12: .25}, "a", 1)
m.add_action(2, {4:1}, "a", 2)
m.add_action(12, {3:1}, "a", 1)
m.add_action(3, {3:.5, 4: .5}, "a", 1)
m.add_action(4, {1:1}, "a", 0)
m.add_action(7, {3:1}, "a", 1)
m.add_action(7, {6:1}, "b", 1)
m.add_action(6, {4:.5, 5:.5}, "a", 5)
m.add_action(5, {1:1}, "a", 6)
m.add_action(8, {9:1}, "a", 1)
m.add_action(8, {1:1}, "b", 3)
m.add_action(10, {1:.5, 11:.5}, "a", 2)
m.add_action(0, {0:1}, "r", 0)
m.add_action(9, {9:1}, "r", 0)
m.add_action(11, {11:1}, "a", 1)

MI = BasicES(m)
m.energy_levels = MI
# -

result   = MI.get_minInitCons()
expected = [0, 3, 2, 1, 3, 9, 14, 1, 1, 0, 5, 1, 1]
m.show()

assert result == expected, ("BasicES.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for BasicES.get_minInitCons() in test_safety file.")

# If state 11 is not a reload state, we cannot reach reload from 10 for sure.

# +
m.unset_reload(11)

result = MI.get_minInitCons(recompute=True)
expected = [0, 3, 2, 1, 3, 9, 14, 1, 1, 0, inf, inf, 1]
m.energy_levels = MI
m.show()
# -

assert result == expected, ("BasicES.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for BasicES.get_minInitCons() in test_safety file.")

# ### Test BasicES with capacity

MI.cap=14
result = MI.get_minInitCons(recompute=True)
result2 = m.get_minInitCons(14)
expected = [0, 3, 2, 1, 3, 9, 14, 1, 1, 0, inf, inf, 1]
m.show()

assert result == result2, ("result and result2 should be the same\n" +
    f"  result  : {result}\n" +
    f"  result2 : {result2}\n")
print("Passed test 3 for BasicES.get_minInitCons() in test_safety file.")

assert result == expected, ("BasicES.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for BasicES.get_minInitCons() in test_safety file.")

# Decreasing capacity should "kill" state 6

result = m.get_minInitCons(capacity=13)
expected = [0, 3, 2, 1, 3, 9, inf, 1, 1, 0, inf, inf, 1]
m.show()

assert result == expected, ("BasicES get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 5 for BasicES.get_minInitCons() in test_safety file.")

# ## Test safe reloads
# Reloads should have red 0, otherwise the red and orange should be the same in this case.

result = m.get_safe(14)
expected = [0, 3, 2, 0, 0, 9, 14, 1, 1, 0, inf, inf, 1]
m.show()

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for get_safe() in test_safety file.")

# ### version with LeastFixpoint

m.energy_levels = LeastFixpointES(m, 14)
result = m.get_safe(14)
m.show()

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 2 for get_safe() in test_safety file.")

# ### Test propagation of useless reloads
# Change the consumption on the action of st. 3. This makes state 3 an useless reload

# +
a = next(m.actions_for_state(3))
a.cons = 15
m.structure_change()

result = m.get_safe(14)
expected = [0, inf, inf, inf, inf, inf, inf, inf, 1, 0, inf, inf, inf]
m.show()
# -

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 3 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = LeastFixpointES(m, 14)
result = m.get_safe(14)
assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 1 for LeastFixpointES() in test_safety file.")

# ## Reload that is never safe
# safe_values = ∞ even with cap = ∞, which is different from minInitCons (orange)

m = consMDP.ConsMDP()
m.new_states(4)
m.set_reload(2)
m.set_reload(0)
m.add_action(0, {0:1}, "", 1)
m.add_action(1, {0:1}, "a", 1000)
m.add_action(1, {2:1}, "b", 1)
m.add_action(3, {3:1}, "r", 1010)
m.add_action(1, {3:1}, "r", 1)
m.add_action(2, {3:1}, "r", 1)

result = m.get_safe()
expected = [0, 1000, inf, inf]
m.show()

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 4 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = LeastFixpointES(m)
result = m.get_safe()
assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 5 for get_safe() in test_safety file.")

# ## Test safe_values[r] = cap for a reload
# The reload should get 0. This was incorrect for some time.

# +
from reachability_examples import little_alsure
m, T = little_alsure()

result = m.get_safe(3)
expected = [2, 1, 2, 0]
m.show()
# -

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n" +
    "Perhaps some reload should be 0 and is not")
print("Passed test 6 for get_safe() in test_safety file.")

# # Example of incorrectness of the least fixpoint algorithm bounded by $|S|$ steps

m = consMDP.ConsMDP()
m.new_state(True)
m.new_states(2)
m.add_action(0, {0:1}, "", 0)
m.add_action(1, {0:1}, "a", 1000)
m.add_action(1, {2:1}, "b", 1)
m.add_action(2, {1:1}, "b", 1)
MI = BasicES(m)
m.energy_levels = MI

result = MI.get_minInitCons()
expected = [0,1000,1001]
m.show()

assert result == expected, ("BasicES.get_minInitCons() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 6 for BasicES.get_minInitCons() in test_safety file.")

# # Example of the incorrectness of bounding SafeReloads by $|S|$ iterations
# The original idea that we can bound the number of iterations by $|S|$ is incorrect. The following example used to give value 1 for state 2.

# +
m = consMDP.ConsMDP()
m.new_state(True)
m.new_states(2)
m.new_state(True)
m.add_action(0, {0:1}, "", 1)
m.add_action(1, {0:1}, "a", 1000)
m.add_action(1, {2:1}, "b", 1)
m.add_action(2, {1:1}, "b", 1)
m.add_action(3, {3:1}, "r", 1010)
m.add_action(1, {3:1}, "r", 1)
m.add_action(2, {3:1}, "r", 1)

result = m.get_safe(1005)
expected = [0, 1000, 1001, inf]
m.show()
# -

assert result == expected, ("EnergyLevels.get_safe() returns" +
    " wrong values:\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 7 for get_safe() in test_safety file.")

# Test the version with LeastFixpoint
m.energy_levels = LeastFixpointES(m, 1005)
result = m.get_safe()
m.show()

assert result == expected, ("Safe reloads are wrong.\n" +
    f"  expected: {expected}\n  returns:  {result}\n")
print("Passed test 8 for get_safe() in test_safety file.")
