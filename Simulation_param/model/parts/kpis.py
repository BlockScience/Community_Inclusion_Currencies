
import numpy as np
from .initialization import *
from .supportingFunctions import *
import networkx as nx


# Behaviors
def kpis(params, step, sL, s):
    ''''''
    # instantiate network state
    network = s['network']

    KPIDemand = {}
    KPISpend = {}
    KPISpendOverDemand = {}
    for i in mixingAgents:
        demand = []
        for j in network.adj[i]:
            try:
                demand.append(network.adj[i][j]['demand'])
            except:
                pass

        spend = []
        for j in network.adj[i]:
            try:
                spend.append(network.adj[i][j]['spend'])
            except:
                pass

        sumDemand = sum(demand)
        sumSpend = sum(spend)
        try:
            spendOverDemand = sumSpend/sumDemand
        except:
            spendOverDemand = 0

        KPIDemand[i] = sumDemand
        KPISpend[i] = sumSpend
        KPISpendOverDemand[i] = spendOverDemand

    #print(nx.katz_centrality_numpy(G=network,weight='spend'))
    return {'KPIDemand':KPIDemand,'KPISpend':KPISpend,'KPISpendOverDemand':KPISpendOverDemand}

def velocity_of_money(params, step, sL, s):
    ''''''
    # instantiate network state
    network = s['network']

    KPISpend = s['KPISpend']

    # TODO: Moving average for state variable
    T = []
    for i,j in KPISpend.items():
        T.append(j)
        
    T = sum(T)
    
    # TODO Moving average for state variable 
    M = []
    for i in agents:
        M.append(network.nodes[i]['tokens'] + network.nodes[i]['native_currency'])
        
    M = sum(M)
    
    V_t = (priceLevel *T)/M

    return {'V_t':V_t,'T':T,'M':M}


# Mechanisms
def update_KPIDemand(params, step, sL, s,_input):
    y = 'KPIDemand'
    x = _input['KPIDemand']
    return (y,x)

def update_KPISpend(params, step, sL, s,_input):
    y = 'KPISpend'
    x = _input['KPISpend']
    return (y,x)

def update_KPISpendOverDemand(params, step, sL, s,_input):
    y = 'KPISpendOverDemand'
    x = _input['KPISpendOverDemand']
    return (y,x)


def update_velocity_of_money(params, step, sL, s,_input):
    y = 'VelocityOfMoney'
    x = _input['V_t']
    return (y,x)
