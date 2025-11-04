# psuedo code for podem.py module

"""
backtrace function

To justify line k for value vk, generate Objective(k, vk)
--> Returns a PI assignment (j, vj) to achieve the objective

Backtracing maps an objective int a PI assignment


Backtrace (k, vk) # Recursive generation objectives until it reaches PI
    v = vk
    while k is a gate output # k is not PI
        i = inversion of k
        select an input j of k with value x
        v = v XOR i
        k = j
        if k i PI then return (k, v)

Objective()
begin
    /* the target fault is l s-a-v */
    if (the value of l is x) then return (l, v')
     
    # Find the necessary inputs to propagate the fault
    select a gate (G) from the D-frontier
    select an input (j) of G with value x
    c = controlling value of G

    return (j, c') 

PODEM() # All lines are initialized to x
1. if (error at PO) then return SUCCESS
2. if (test not possible) then return FAILURE
3. (k, vk) = Objective()
4. (j, vj) = Backtrace(k, vk) # j is a PI
5. Imply(j, vj) # 5-value simulation with PI assignments
6. if PODEM() == SUCCESS then return SUCCESS
7. Imply(j, vj') # reverse decision
8. if PODEM() == SUCCESS then return SUCCESS
9. Imply (j, x) # reverse j to x
10. return FAILURE # D-frontier becomes empty
"""