# this keeps track of the failed experiments, or experiments that
# simply take too long to run

# now define TC0 to TC5
CONTROL = dict(n_agents=50, door_width=1.2, n_exits=1, room_size=20.0, panic_speed=1.5)
MODELS = ['baseline', 'behavioral', 'group']
N_RUNS = 3
MAX_STEPS = 2000

'''
3 runs & max steps of 2000 is too much.
keep track of the no. of agents escaped per unit time instead.
maybe keep it to 3 runs & max 800 steps, and get the corresponding
fraction, take out the NaN also
'''

# this is the experimentation that cause IDE to crash
TEST_CASES = {
    "TC0": {"var": "control",     "values": [None]},
    "TC1": {"var": "n_agents",    "values": [50, 100, 500]},
    "TC2": {"var": "door_width",  "values": [1.0, 1.2, 1.6]},
    "TC3": {"var": "n_exits",     "values": [1, 2, 3]},
    "TC4": {"var": "room_size",   "values": [16.0, 20.0, 24.0]},
    "TC5": {"var": "panic_speed", "values": [1.5, 2.0, 3.0]},
}


# the failed run
rows = []

for tc, spec in TEST_CASES.items():
    var, vals = spec["var"], spec["values"]
    for model in MODELS:
        for v in vals:
            for r in range(N_RUNS):
                params = CONTROL.copy()
                if var != "control":
                    params[var] = v

                out = run_control_extended(
                    model=model,
                    max_steps=MAX_STEPS,
                    seed=1000 + r,
                    **params
                )
                out["test_case"] = tc
                out["changed_var"] = var
                out["changed_value"] = "control" if var == "control" else v
                rows.append(out)

df_all = pd.DataFrame(rows)
df_all.head(12)