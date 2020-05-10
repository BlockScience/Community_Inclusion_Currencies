
import numpy as np
import pandas as pd
from cadCAD.configuration.utils import access_block
from .initialization import *
from .supportingFunctions import *
from collections import OrderedDict

# Parameters
agentsMinus = 2
# percentage of balance a user can redeem
redeemPercentage = 0.5

# Behaviors
def choose_agents(params, step, sL, s):
    '''
    Choose agents to interact during the given timestep and create their demand from a uniform distribution. 
    Based on probability, choose utility. 
    '''
    outboundAgents = np.random.choice(mixingAgents,size=len(mixingAgents)-agentsMinus).tolist()
    inboundAgents = np.random.choice(mixingAgents,size=len(mixingAgents)-agentsMinus).tolist()
    stepDemands = np.random.uniform(low=1, high=500, size=len(mixingAgents)-agentsMinus).astype(int)
    

    stepUtilities = np.random.choice(list(UtilityTypesOrdered.keys()),size=len(mixingAgents)-agentsMinus,p=list(utilityTypesProbability.values())).tolist()

    return {'outboundAgents':outboundAgents,'inboundAgents':inboundAgents,'stepDemands':stepDemands,'stepUtilities':stepUtilities}


def spend_allocation(params, step, sL, s):
    '''
    Take mixing agents, demand, and utilities and allocate agent shillings and tokens based on utility and scarcity. 
    '''
    # instantiate network state
    network = s['network']

    spendI = []
    spendJ = []
    spendAmount = []

    # calculate max about of spend available to each agent
    maxSpendShilling = {}
    for i in mixingAgents:
        maxSpendShilling[i] = network.nodes[i]['native_currency']
        
    maxSpendCIC = {}
    for i in mixingAgents:
        maxSpendCIC[i] = network.nodes[i]['tokens']


    for i in mixingAgents: 
        rankOrder = {}
        rankOrderDemand = {}
        for j in network.adj[i]:
            try:
                rankOrder[j] = UtilityTypesOrdered[network.adj[i][j]['utility']]
                rankOrderDemand[j] = network.adj[i][j]['demand']
                rankOrder = dict(OrderedDict(sorted(rankOrder.items(), key=lambda v: v, reverse=False)))
                for k in rankOrder:
                    # if i or j is external, we transact 100% in shilling
                    if i == 'external':
                        amt = spendCalculationExternal(i,j,rankOrderDemand,maxSpendShilling)
                        spendI.append(i)
                        spendJ.append(j)
                        spendAmount.append(amt)
                        maxSpendShilling[i] = maxSpendShilling[i] - amt 
                    elif j == 'external':
                        amt = spendCalculationExternal(i,j,rankOrderDemand,maxSpendShilling)
                        spendI.append(i)
                        spendJ.append(j)
                        spendAmount.append(amt)
                        maxSpendShilling[i] = maxSpendShilling[i] - amt 
                    else:
                        amt = spendCalculation(i,j,rankOrderDemand,maxSpendShilling,maxSpendCIC,fractionOfDemandInCIC)
                        spendI.append(i)
                        spendJ.append(j)
                        spendAmount.append(amt)
                        maxSpendShilling[i] = maxSpendShilling[i] - amt * (1- fractionOfDemandInCIC)
                        maxSpendCIC[i] = maxSpendCIC[i] - (amt * fractionOfDemandInCIC)
            except:
                pass
    return {'spendI':spendI,'spendJ':spendJ,'spendAmount':spendAmount}


def withdraw_calculation(params, step, sL, s):
    ''''''
    # instantiate network state
    network = s['network']

    # Assumptions:
    # * user is only able to withdraw up to 50% of balance, assuming they have spent 50% of balance
    # * Agents will withdraw as much as they can.
    withdraw = {}

    fiftyThreshold = {}

    startingBalance = s['startingBalance']

    spend = s['30_day_spend']
    timestep = s['timestep']

    division =  timestep % 30  == 0

    if division == True:
        for i,j in startingBalance.items():
            fiftyThreshold[i] = j * 0.5
        if s['timestep'] > 7:
            for i,j in fiftyThreshold.items():
                if spend[i] > 0 and fiftyThreshold[i] > 0:
                    if spend[i] * fractionOfActualSpendInCIC >= fiftyThreshold[i]:
                        spent = spend[i]
                        amount = spent * redeemPercentage
                        if network.nodes[i]['tokens'] > amount:
                            withdraw[i] = amount
                        elif  network.nodes[i]['tokens'] < amount:
                            withdraw[i] = network.nodes[i]['tokens']
                    else:
                        pass
                else:
                    pass
        else:
            pass
    else:
        pass


    return {'withdraw':withdraw}

# Mechanisms 
def update_agent_activity(params,step,sL,s,_input):
    '''
    Update the network for interacting agent, their demand, and utility.
    '''
    y = 'network'
    network = s['network']

    outboundAgents = _input['outboundAgents']
    inboundAgents = _input['inboundAgents']
    stepDemands = _input['stepDemands']
    stepUtilities = _input['stepUtilities']
    
    # create demand edge weights
    try:
        for i,j,l in zip(outboundAgents,inboundAgents,stepDemands):
            network[i][j]['demand'] = l
    except:
        pass

    # Create cic % edge weights
    try:
        for i,j in zip(outboundAgents,inboundAgents):
            # if one of the agents is external, we will transact in 100% shilling
            if i == 'external':
                network[i][j]['fractionOfDemandInCIC'] = 1
            elif j == 'external':
                network[i][j]['fractionOfDemandInCIC'] = 1
            else:
                network[i][j]['fractionOfDemandInCIC'] = fractionOfDemandInCIC
    except:
        pass

    # Create utility edge types
    try: 
        for i,j,l in zip(outboundAgents,inboundAgents,stepUtilities):
            network[i][j]['utility'] = l
    except:
        pass

    x = network
    return (y,x)


def update_outboundAgents(params,step,sL,s,_input):
    '''
    Update outBoundAgents state variable
    '''
    y = 'outboundAgents'

    x = _input['outboundAgents']

    return (y,x)

def update_inboundAgents(params,step,sL,s,_input):
    '''
    Update inBoundAgents state variable
    '''
    y = 'inboundAgents'

    x = _input['inboundAgents']
    return (y,x)


def update_node_spend(params, step, sL, s,_input):
    '''
    Update network with actual spend of agents.
    '''
    y = 'network'
    network = s['network']
    
    spendI = _input['spendI']
    spendJ = _input['spendJ']
    spendAmount = _input['spendAmount']

    for i,j,l in zip(spendI,spendJ,spendAmount):   
        network[i][j]['spend'] = l
        if i == 'external':
            network[i][j]['fractionOfActualSpendInCIC'] = 1
        elif j == 'external':
            network[i][j]['fractionOfActualSpendInCIC'] = 1
        else:
            network[i][j]['fractionOfActualSpendInCIC'] = fractionOfActualSpendInCIC

    outflowSpend, inflowSpend = iterateEdges(network,'spend')

    for i, j in inflowSpend.items():
        if i == 'external':
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] +  inflowSpend[i]
        elif j == 'external':
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] +  inflowSpend[i]
        else:
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] +  inflowSpend[i] * (1- fractionOfDemandInCIC)
            network.nodes[i]['tokens'] = network.nodes[i]['tokens'] + (inflowSpend[i] * fractionOfDemandInCIC)
        
    for i, j in outflowSpend.items():
        if i == 'external':
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] - outflowSpend[i]
        elif j == 'external':
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] - outflowSpend[i]
        else:
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] - outflowSpend[i]* (1- fractionOfDemandInCIC)
            network.nodes[i]['tokens'] = network.nodes[i]['tokens'] - (outflowSpend[i] * fractionOfDemandInCIC)

    # Store the net of the inflow and outflow per step
    network.nodes['external']['delta_native_currency'] = sum(inflowSpend.values()) - sum(outflowSpend.values())

    x = network
    return (y,x)


def update_withdraw(params, step, sL, s,_input):
    '''
    Update flow sstate variable with the aggregated amount of shillings withdrawn
    '''
    y = 'withdraw'
    x = s['withdraw']
    if _input['withdraw']:
        x = _input['withdraw']
    else:
        x = 0

    return (y,x)

def update_network_withraw(params, step, sL, s,_input):
    '''
    Update network for agents withdrawing 
    '''
    y = 'network'
    network = s['network']
    withdraw = _input['withdraw']

    if withdraw:
        for i,j in withdraw.items():
            # update agent nodes
            network.nodes[i]['tokens'] = network.nodes[i]['tokens'] - j
            network.nodes[i]['native_currency'] = network.nodes[i]['native_currency'] + (j * leverage)

        withdrawnCICSum = []
        for i,j in withdraw.items():
            withdrawnCICSum.append(j)
        
        # update cic node
        network.nodes['cic']['native_currency'] = network.nodes[i]['native_currency'] - (sum(withdrawnCICSum) * leverage)
        network.nodes['cic']['tokens'] = network.nodes[i]['tokens'] + (sum(withdrawnCICSum) * leverage)

    else:
        pass
    x = network
    return (y,x)

