from ortools.graph import pywrapgraph

CAPACITY_PER_EDGE = 1000000000


def preprocess_graph(G):
    # Add node indices and diff values
    for i, node in enumerate(G.nodes()):
        G.node[node]['index'] = i
        if 'diff' not in G.node[node]:
            G.node[node]['diff'] = 0


def setup_min_cost_flow(G, cost_field):
    # Set up the optimisation problem
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    for edge in G.edges(data=True):
        min_cost_flow.AddArcWithCapacityAndUnitCost(G.node[edge[0]]['index'], G.node[edge[1]]['index'],
                                                    CAPACITY_PER_EDGE, edge[2][cost_field])
        min_cost_flow.AddArcWithCapacityAndUnitCost(G.node[edge[1]]['index'], G.node[edge[0]]['index'],
                                                    CAPACITY_PER_EDGE, edge[2][cost_field])

    for node in G.nodes():
        if G.node[node]['diff'] != 0:
            test = node
        min_cost_flow.SetNodeSupply(
            G.node[node]['index'], G.node[node]['diff'])

    return min_cost_flow


def solve_min_cost_flow(G, cost_field):
    # TODO add relevant data to the graph

    preprocess_graph(G)
    min_cost_flow = setup_min_cost_flow(G, cost_field)

    if min_cost_flow.SolveMaxFlowWithMinCost() == min_cost_flow.OPTIMAL:
        print('Minimum cost:', min_cost_flow.OptimalCost())
        print('')
        print('  Arc    Flow / Capacity  Cost')
        for i in range(min_cost_flow.NumArcs()):
            cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
            print('%1s -> %1s   %3s  / %3s       %3s' % (
                min_cost_flow.Tail(i),
                min_cost_flow.Head(i),
                min_cost_flow.Flow(i),
                min_cost_flow.Capacity(i),
                cost))
    else:
        print('There was an issue with the min cost flow input.')
