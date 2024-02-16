from ortools.sat.python import cp_model


def assign_rides(rides: list[tuple[int,int]], max_running_time: int=30):
    model = cp_model.CpModel()
    num_rides = len(rides)
    durations = [end-start for start, end in rides]
    chosen_car_vars = [model.NewIntVar(0, num_rides-1, f'car_{i}') for i in range(num_rides)]
    for i in range(num_rides):
        for j in range(i+1, num_rides):
            start_i, end_i = rides[i]
            start_j, end_j = rides[j]
            if not (end_i <= start_j or end_j <= start_i):
                model.Add(chosen_car_vars[i] != chosen_car_vars[j])
    nb_used_cars_var = model.NewIntVar(0, num_rides-1, 'nb_used_cars')
    model.AddMaxEquality(nb_used_cars_var, chosen_car_vars)
    model.Minimize(nb_used_cars_var)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = int(max_running_time*0.3)
    status = solver.Solve(model)
    print(solver.StatusName(status))
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN):
        return None, None
    
    nb_needed_cars = solver.Value(nb_used_cars_var)+1
    model = cp_model.CpModel()
    chosen_car_vars = [model.NewIntVar(0, nb_needed_cars-1, f'car_{i}') for i in range(num_rides)]
    for i in range(num_rides):
        for j in range(i+1, num_rides):
            start_i, end_i = rides[i]
            start_j, end_j = rides[j]
            if not (end_i <= start_j or end_j <= start_i):
                model.Add(chosen_car_vars[i] != chosen_car_vars[j])
    car_durations = [model.NewIntVar(0, sum(durations), f'duration_{i}') for i in range(nb_needed_cars)]
    ride_car_vars = {}
    for i in range(num_rides):
        for j in range(nb_needed_cars):
            ride_car_vars[(i, j)] = model.NewBoolVar(f'ride_{i}_car_{j}')
            model.Add(chosen_car_vars[i] == j).OnlyEnforceIf(ride_car_vars[(i, j)])
            model.Add(chosen_car_vars[i] != j).OnlyEnforceIf(ride_car_vars[(i, j)].Not())
    for j in range(nb_needed_cars):
        model.Add(sum(ride_car_vars[(i, j)]*durations[i] for i in range(num_rides)) == car_durations[j])
    max_car_duration = model.NewIntVar(0, sum(durations), 'max_car_duration')
    min_car_duration = model.NewIntVar(0, sum(durations), 'min_car_duration')
    model.AddMaxEquality(max_car_duration, car_durations)
    model.AddMinEquality(min_car_duration, car_durations)
    model.Minimize(max_car_duration - min_car_duration)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = int(max_running_time*0.7)
    status = solver.Solve(model)
    print(solver.StatusName(status))
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN):
        return None, None
    car_assignments = [solver.Value(chosen_car_vars[i]) for i in range(num_rides)]
    car_durations = [solver.Value(duration) for duration in car_durations]
    return car_assignments, car_durations
