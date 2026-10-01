#cstar
#import arity0
#import arity1
#import arity2



CountSep = # "@"

InInit = (CountSep == 0)
InPlan = (CountSep == 1)
InGoal = (CountSep == 2)
End = (CountSep == 3)

T_clear = ("unstack" || "putdown" || "stack")
T_holding = ("pickup" || "unstack")
T_on = ("stack")
T_on_table = ("putdown")
T_handempty = ("putdown"|| "stack")

F_clear =  ("stack" || "unstack" || "pickup")
F_holding = ("putdown" || "stack")
F_on = ("unstack")
F_on_table = ("pickup")
F_handempty = ("pickup" || "unstack")

Pre_clear = ("unstack" || "stack" || "pickup")
Pre_holding = ("putdown" || "stack")
Pre_on = ("unstack")
Pre_on_table = ("pickup")
Pre_handempty = ("pickup"|| "unstack")

Curr_pickup = (# [arity1] "pickup") > 0
Curr_putdown = (# [arity1] "putdown") > 0
Curr_stack = (# [arity2] "stack") > 0
Curr_unstack = (# [arity2] "unstack") > 0

Curr_clear = (# [arity1] "clear") > 0
Curr_holding = (# [arity1] "holding") > 0
Curr_on = (# [arity2] "on") > 0
Curr_on_table = (# [arity1] "on-table") > 0
Curr_handempty = (# [arity0] "handempty") > 0

V_init_unstack_clear = (# [j < i, match([(0, 1, 0)])] (InInit && Curr_clear)) if Curr_unstack else 0
V_add_unstack_clear = (# [j < i, match([(0, 1, 0)])] (Curr_unstack || Curr_putdown) + # [j < i, match([(1, 1, 0)])] Curr_stack) if Curr_unstack else 0
V_del_unstack_clear = (# [j < i, match([(0, 1, 0)])] (Curr_stack || Curr_pickup)) if Curr_unstack else 0

V_init_stack_clear = (# [j < i, match([(0, 0, 0)])] (InInit && Curr_clear)) if Curr_stack else 0
V_add_stack_clear = (# [j < i, match([(0, 0, 0)])] (Curr_unstack || Curr_putdown) + # [j < i, match([(1, 0, 0)])] Curr_stack) if Curr_stack else 0
V_del_stack_clear = (# [j < i, match([(0, 0, 0)])] (Curr_stack || Curr_pickup)) if Curr_stack else 0

V_init_pickup_clear = (# [j < i, match([(0, 0, 0)])] (InInit && Curr_clear)) if Curr_pickup else 0
V_add_pickup_clear = (# [j < i, match([(0, 0, 0)])] (Curr_unstack || Curr_putdown) + # [j < i, match([(1, 0, 0)])] Curr_stack) if Curr_pickup else 0
V_del_pickup_clear = (# [j < i, match([(0, 0, 0)])] (Curr_stack || Curr_pickup)) if Curr_pickup else 0

V_init_putdown_holding = (# [j < i, match([(0, 0, 0)])] (InInit && Curr_holding)) if Curr_putdown else 0
V_add_putdown_holding = (# [j < i, match([(0, 0, 0)])] Curr_pickup + # [j < i, match([(1, 0, 0)])] Curr_unstack) if Curr_putdown else 0
V_del_putdown_holding = (# [j < i, match([(0, 0, 0)])] Curr_putdown + # [j < i, match([(1, 0, 0)])] Curr_stack) if Curr_putdown else 0

V_init_stack_holding = (# [j < i, match([(0, 1, 0)])] (InInit && Curr_holding)) if Curr_stack else 0
V_add_stack_holding = (# [j < i, match([(0, 1, 0)])] Curr_pickup + # [j < i, match([(1, 1, 0)])] Curr_unstack) if Curr_stack else 0
V_del_stack_holding = (# [j < i, match([(0, 1, 0)])] Curr_putdown + # [j < i, match([(1, 1, 0)])] Curr_stack) if Curr_stack else 0

V_init_unstack_on = (# [j < i, match([(1, 1, 0), (0, 0, 0)])] (InInit && Curr_on)) if Curr_unstack else 0
V_add_unstack_on = (# [j < i, match([(1, 1, 0), (0, 0, 0)])] Curr_stack) if Curr_unstack else 0
V_del_unstack_on = (# [j < i, match([(1, 1, 0), (0, 0, 0)])] Curr_unstack) if Curr_unstack else 0

V_init_pickup_on_table = (# [j < i, match([(0, 0, 0)])] (InInit && Curr_on_table)) if Curr_pickup else 0
V_add_pickup_on_table = (# [j < i, match([(0, 0, 0)])] Curr_putdown) if Curr_pickup else 0
V_del_pickup_on_table = (# [j < i, match([(0, 0, 0)])] Curr_pickup) if Curr_pickup else 0

V_init_pickup_handempty = (# [j < i, match([])] (InInit && Curr_handempty)) if Curr_pickup else 0
V_add_pickup_handempty = (# [j < i, match([])] (Curr_putdown || Curr_stack)) if Curr_pickup else 0
V_del_pickup_handempty = (# [j < i, match([])] (Curr_pickup || Curr_unstack)) if Curr_pickup else 0

V_init_unstack_handempty = (# [j < i, match([])] (InInit && Curr_handempty)) if Curr_unstack else 0
V_add_unstack_handempty = (# [j < i, match([])] (Curr_putdown || Curr_stack)) if Curr_unstack else 0
V_del_unstack_handempty = (# [j < i, match([])] (Curr_pickup || Curr_unstack)) if Curr_unstack else 0

G_init_clear = # [match([(0, 0, 0)])] (InInit && Curr_clear)
G_add_clear = # [match([(0, 0, 0)])] (InPlan && (Curr_unstack || Curr_putdown)) + # [match([(1, 0, 0)])] (InPlan && Curr_stack)
G_del_clear = # [match([(0, 0, 0)])] (InPlan && (Curr_stack || Curr_pickup))

G_init_holding = # [match([(0, 0, 0)])] (InInit && Curr_holding)
G_add_holding = # [match([(0, 0, 0)])] (InPlan && Curr_pickup) + # [match([(1, 0, 0)])] (InPlan && Curr_unstack)
G_del_holding = # [match([(0, 0, 0)])] (InPlan && Curr_putdown) + # [match([(1, 0, 0)])] (InPlan && Curr_stack)

G_init_on = # [match([(1, 1, 0), (0, 0, 0)])] (InInit && Curr_on)
G_add_on = # [match([(1, 1, 0), (0, 0, 0)])] (InPlan && Curr_stack)
G_del_on = # [match([(1, 1, 0), (0, 0, 0)])] (InPlan && Curr_unstack)

G_init_on_table = # [match([(0, 0, 0)])] (InInit && Curr_on_table)
G_add_on_table = # [match([(0, 0, 0)])] (InPlan && Curr_putdown)
G_del_on_table = # [match([(0, 0, 0)])] (InPlan && Curr_pickup)

G_init_handempty = # [match([])] (InInit && Curr_handempty)
G_add_handempty = # [match([])] (InPlan && (Curr_putdown || Curr_stack))
G_del_handempty = # [match([])] (InPlan && (Curr_pickup || Curr_unstack))

GoalSat_clear = (!Curr_clear) || ((G_init_clear + G_add_clear - G_del_clear) == 1)
GoalSat_holding = (!Curr_holding) || ((G_init_holding + G_add_holding - G_del_holding) == 1)
GoalSat_on = (!Curr_on) || ((G_init_on + G_add_on - G_del_on) == 1)
GoalSat_on_table = (!Curr_on_table) || ((G_init_on_table + G_add_on_table - G_del_on_table) == 1)
GoalSat_handempty = (!Curr_handempty) || ((G_init_handempty + G_add_handempty - G_del_handempty) == 1)
Goal_violations = # (InGoal && !(GoalSat_clear && GoalSat_holding && GoalSat_on && GoalSat_on_table && GoalSat_handempty))

Satisfied_unstack_clear = (V_init_unstack_clear + V_add_unstack_clear - V_del_unstack_clear) == 1
Satisfied_unstack_on = (V_init_unstack_on + V_add_unstack_on - V_del_unstack_on) == 1
Satisfied_unstack_handempty = (V_init_unstack_handempty + V_add_unstack_handempty - V_del_unstack_handempty) == 1
Satisfied_stack_clear = (V_init_stack_clear + V_add_stack_clear - V_del_stack_clear) == 1
Satisfied_stack_holding = (V_init_stack_holding + V_add_stack_holding - V_del_stack_holding) == 1
Satisfied_pickup_clear = (V_init_pickup_clear + V_add_pickup_clear - V_del_pickup_clear) == 1
Satisfied_pickup_on_table = (V_init_pickup_on_table + V_add_pickup_on_table - V_del_pickup_on_table) == 1
Satisfied_pickup_handempty = (V_init_pickup_handempty + V_add_pickup_handempty - V_del_pickup_handempty) == 1
Satisfied_putdown_holding = (V_init_putdown_holding + V_add_putdown_holding - V_del_putdown_holding) == 1

Valid_unstack = (!Curr_unstack) || (Satisfied_unstack_clear && Satisfied_unstack_on && Satisfied_unstack_handempty)
Valid_stack = (!Curr_stack) || (Satisfied_stack_clear && Satisfied_stack_holding)
Valid_pickup = (!Curr_pickup) || (Satisfied_pickup_clear && Satisfied_pickup_on_table && Satisfied_pickup_handempty)
Valid_putdown = (!Curr_putdown) || Satisfied_putdown_holding

Preconditions_ok = (# ! Valid_unstack == 0) && (# ! Valid_stack == 0) && (# ! Valid_pickup == 0) && (# ! Valid_putdown == 0)
Goals_reached = Goal_violations == 0
AllActionsValid = End && Preconditions_ok
AllGoalsSatisfied = End && Goals_reached
Plan_valid = AllActionsValid && AllGoalsSatisfied