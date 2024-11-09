from typing import List, Dict, Tuple


Sources = List[int]
Destinations = List[int]
Supply = Dict[int, float]
Demand = Dict[int, float]
CPU = Dict[Tuple[int, int], float]


def display_problem(
        sources: Sources,
        destinations: Destinations,
        supply: Supply,
        demand: Demand,
        cost_per_unit: CPU,
):
    """
    Print the transportation problem statement
    """
    print("SRC\\DST", *destinations, "Supply", sep="\t")
    for s in sources:
        print(
            s,
            *(cost_per_unit[(s, d)] for d in destinations),
            supply[s],
            sep="\t"
        )
    print("Demand", *(demand[d] for d in destinations), sep="\t")


def is_valid(
        sources: Sources,
        destinations: Destinations,
        supply: Supply,
        demand: Demand,
        cost_per_unit: CPU,
):
    return sum(supply.values()) == sum(demand.values())


def isApplicable(cost, supply, demand): # check is problem applicable
    for i in cost: #if in cost no negative values
        for j in i:
            if j < 0:
                return False
    for i in supply: # if in supply no negative values
        if i < 0:
            return False
    for i in demand: # if in demand no negative values
        if i < 0:
            return False
    #num rows in cost == len(supply) and num columns == len(demand)
    if len(cost) != len(supply):
        return False
    num_colums = len(cost[1])
    if num_colums != len(demand):
        return False
    return True

def ibfs_nw(
        sources: Sources,
        destinations: Destinations,
        supply: Supply,
        demand: Demand,
        cost_per_unit: CPU,
):
    """
    Find an initial basic feasible solution for a given problem by using the North-West corner method
    """
    supply = supply.copy()
    demand = demand.copy()
    sol = 0
    sol_matrix = [[0]*len(demand) for _ in range(len(supply))]
    si = 0
    di = 0
    while (0 <= si < len(sources)) and (0 <= di < len(destinations)):

        s = sources[si]
        d = destinations[di]
        delta = supply[s] - demand[d]
        sol += min(supply[s], demand[d]) * cost_per_unit[(s, d)]
        sol_matrix[s-1][d-1] = min(supply[s], demand[d])
        if delta < 0:
            # supply < demand
            # decrease demand by the supply and
            # and move on to the next supply
            demand[d] -= supply[s]
            si += 1
        elif delta == 0:
            # supply == demand
            # move on to the next demand
            # move on to the next supply
            di += 1
            si += 1
        elif delta > 0:
            # supply > demand
            supply[s] -= demand[d]
            di += 1
    return sol,sol_matrix

def v_a_m(supply, costs, demand):
    num_rows = len(supply)
    num_cols = len(demand)
    solution = 0
    allocation = [[0] * num_cols for _ in range(num_rows)]
    while True:
        by_colums = []
        by_rows = []
        # find row difference
        for i in range(num_rows):
            sortedList = []
            for j in range(num_cols):
                if demand[j] <= 0 or supply[i] <= 0:
                    continue
                sortedList.append(costs[i][j])
            sortedList.sort()
            if len(sortedList) >= 2:
                by_rows.append(sortedList[1] - sortedList[0])
            elif len(sortedList) == 1:
                by_rows.append(0)
            else:
                by_rows.append(-1)

        # find column difference
        for i in range(num_cols):
            sortedList = []
            for j in range(num_rows):
                if supply[j] <= 0 or demand[i] <= 0:
                    continue
                sortedList.append(costs[j][i])
            sortedList.sort()
            if len(sortedList) >= 2:
                by_colums.append(sortedList[1] - sortedList[0])
            elif len(sortedList) == 1:
                by_colums.append(0)
            else:
                by_colums.append(-1)

        #max for row and column difference
        max_in_row = max(by_rows)
        max_in_column = max(by_colums)

        if max_in_row > max_in_column: # if max in row difference
            row_index = by_rows.index(max_in_row) # row index
            column_index = 0
            list = [] # list for values in cost
            for i in range(num_cols):
                if demand[i] <= 0:
                    continue
                list.append(costs[row_index][i])

            mini = min(list) #minimum value

            for i in range(num_cols): #find column index
                if costs[row_index][i] == mini:
                    column_index = i

            #if min value in demand
            if demand[column_index] < supply[row_index] and demand[column_index] != 0:
                allocation[row_index][column_index] = demand[column_index]
                res = mini * demand[column_index]
                supply[row_index] = supply[row_index] - demand[column_index]
                demand[column_index] = 0
                solution += res

            #if min value in supply
            else:
                allocation[row_index][column_index] = supply[row_index]
                res = mini * supply[row_index]
                demand[column_index] = demand[column_index] - supply[row_index]
                supply[row_index] = 0
                solution += res

        else: # if max in column difference
            column_index = by_colums.index(max_in_column) # column_index
            row_index = 0
            list = [] # list for values in cost

            for i in range(num_rows): # add values in list
                if supply[i] <= 0:
                    continue
                list.append(costs[i][column_index])

            mini = min(list) #minimum value

            for i in range(num_rows): #find row index
                if costs[i][column_index] == mini:
                    row_index = i

            # if minimum value in demand
            if demand[column_index] < supply[row_index] and demand[column_index] != 0:
                allocation[row_index][column_index] = demand[column_index]
                res = mini * demand[column_index]
                supply[row_index] = supply[row_index] - demand[column_index]
                demand[column_index] = 0
                solution += res

            #if minimum value in supply
            else:
                allocation[row_index][column_index] = supply[row_index]
                res = mini * supply[row_index]
                demand[column_index] = demand[column_index] - supply[row_index]
                supply[row_index] = 0
                solution += res

        #do while in demand and supply all values not zero
        if all(s == 0 for s in supply) or all(d == 0 for d in demand):
            break

    return solution, allocation




def russel(sources: Sources,
           destinations: Destinations,
           supply: Supply,
           demand: Demand,
           cost_per_unit: CPU,):
    """
    Find an initial basic feasible solution for a given problem by using the Russell's approximation method
    """

    # Convert supply and demand dictionaries to lists for easier manipulation
    sup = list(supply.values())
    dem = list(demand.values())

    # Initialize total solution cost
    sol = 0

    # Create an empty solution matrix filled with zeros
    solution_matrix = [[0]*len(dem) for _ in range(len(sup))]

    # Continue until either all supply or all demand is satisfied
    while sum(sup) != 0 and sum(dem) != 0:

        # Initialize arrays to store maximum costs in rows and columns
        max_in_row = [0]*len(supply)
        max_in_col = [0]*len(demand)

        # Calculate maximum costs in each row and column
        for i in range(len(supply)):
            for j in range(len(demand)):
                if sup[i] != 0 and dem[j] != 0:
                    max_in_row[i] = max(max_in_row[i], cost_per_unit[(i+1,j+1)])
                    max_in_col[j] = max(max_in_col[j], cost_per_unit[(i+1,j+1)])

        # Create a copy of the cost per unit dictionary
        new_cpu = cost_per_unit.copy()

        # Adjust costs based on maximum values in rows and columns
        for i in range(len(supply)):
            for j in range(len(demand)):
                new_cpu[(i+1,j+1)] -= (max_in_row[i] + max_in_col[j])


        s, d = 0, 0
        min_value = 1000000000

        # Find the cell with the minimum adjusted cost
        for k, v in new_cpu.items():
            x, y = k
            if sup[x-1] == 0 or dem[y-1] == 0:
                continue
            if v < min_value:
                min_value = v
                s, d = k


        s -= 1
        d -= 1

        # Calculate the cost for the selected cell
        delta = sup[s] - dem[d]
        sol += min(sup[s], dem[d]) * cost_per_unit[(s+1, d+1)]

        # Update the solution matrix
        solution_matrix[s][d] = min(sup[s], dem[d])

        # Handle supply and demand adjustments
        if delta < 0:
            # Supply less than demand
            # Decrease demand by the supply and move to the next supply
            dem[d] -= sup[s]
            sup[s] = 0
        elif delta == 0:
            # Supply equals demand
            # Move to the next demand and the next supply
            sup[s] = 0
            dem[d] = 0
        elif delta > 0:
            # Supply greater than demand
            # Reduce supply by the demand and move to the next demand
            sup[s] -= dem[d]
            dem[d] = 0

    # Return the total cost and the solution matrix
    return sol, solution_matrix

if __name__ == "__main__":
    print("enter the number of sources")
    n_sources = int(input())
    sources = list(range(1, n_sources + 1))
    print("enter the supply for every source")
    supply = {i: float(x) for i, x in zip(sources, input().split())}
    print("enter the number of destinations")
    n_destinations = int(input())
    destinations = list(range(1, n_destinations + 1))
    print("enter the demand for every destination")
    demand = {i: float(x) for i, x in zip(destinations, input().split())}
    print(
        "enter the cost per unit distributed for every source-destination pair"
    )
    cost = [[0.0 for _ in range(n_destinations)] for _ in range(n_sources)]
    cost_per_unit = {
        (s, d): float(x)
        for s in sources
        for d, x in zip(destinations, input().split())
    }
    for (i, j), value in cost_per_unit.items():
        cost[i - 1][j - 1] = int(value)
    supply2 = []


    print("Transportation problem statement:")
    display_problem(
        sources=sources,
        destinations=destinations,
        supply=supply,
        demand=demand,
        cost_per_unit=cost_per_unit,
    )
    nw_sol,nw_sol_matrix = ibfs_nw(
        sources=sources,
        destinations=destinations,
        supply=supply,
        demand=demand,
        cost_per_unit=cost_per_unit,
    )
    russel_sol,russel_sol_matrix = russel(
        sources=sources,
        destinations=destinations,
        supply=supply,
        demand=demand,
        cost_per_unit=cost_per_unit,
    )

    VogelSolution, matrix = v_a_m(list(supply.values()), cost, list(demand.values()))
    if not isApplicable(cost, list(supply.values()), list(demand.values())):
        print("The methods are not applicable!")
    elif not is_valid(sources=sources,
                      destinations=destinations,
                      supply=supply,
                      demand=demand,
                      cost_per_unit=cost_per_unit
                      ):
        print("The problem is not balanced!")
    else:
        print()
        print("solution for Vogel’s approximation method: " + str(VogelSolution))
        print()
        print("vectors for Vogel’s approximation method:")
        for i in matrix:
            for j in i:
                print(j,end=" ")
            print()
        print(f"NW SOL: {nw_sol}")
        print("NW vectors of initial basic feasible solution:")
        for i in nw_sol_matrix:
            for j in i:
                print(j,end=" ")
            print()
        print(f"Russell's approximation method SOL: {russel_sol}")
        print("Russell's approximation method vectors of initial basic feasible solution:")
        for i in russel_sol_matrix:
            for j in i:
                print(j,end=" ")
            print()
