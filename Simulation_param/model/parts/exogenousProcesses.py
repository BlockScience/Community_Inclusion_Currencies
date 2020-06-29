# import numpy as np
# import pandas as pd
from Simulation_param.model.parts.initialization import *
from Simulation_param.model.parts.supportingFunctions import *
    

def startingBalance(params, step, sL, s, _input):
    '''
    Calculate agent starting balance every 30 days
    '''
    y = 'startingBalance'
    network = s['network']

    startingBalance = {}

    timestep = s['timestep']

    division =  timestep % 31  == 0

    if timestep == 1:
        for i in clusters:
            startingBalance[i] = network.nodes[i]['tokens']
    elif division == True:
        for i in clusters:
            startingBalance[i] = network.nodes[i]['tokens']
    else:
        startingBalance = s['startingBalance']
    x = startingBalance

    return (y, x)

def update_30_day_spend(params, step, sL, s,_input):
    '''
    Aggregate agent spend. Refresh every 30 days.
    '''
    y = '30_day_spend'
    network = s['network']

    timestep = s['timestep']

    division =  timestep % 31  == 0

    if division == True:
        outflowSpend, inflowSpend = iterateEdges(network,'spend')
        spend =  outflowSpend 
    else:
        spendOld = s['30_day_spend']
        outflowSpend, inflowSpend = iterateEdges(network,'spend')
        spend = DictionaryMergeAddition(spendOld,outflowSpend) 

    x = spend
    return (y, x)

def redCrossDrop(params, step, sL, s, _input):
    '''
    Every 30 days, the red cross drips to the grassroots operator node
    '''
    y = 'operatorFiatBalance'
    fiatBalance = s['operatorFiatBalance']
    
    timestep = s['timestep']
    
    division =  timestep % params['drip_frequency']  == 0

    if division == True:
        fiatBalance = fiatBalance + drip
    else:
        pass

    x = fiatBalance
    return (y, x)

def clear_agent_activity(params,step,sL,s,_input):
    '''
    Clear agent activity from the previous timestep
    '''
    y = 'network'
    network = s['network']

    if s['timestep'] > 0:
        outboundAgents = s['outboundAgents']
        inboundAgents = s['inboundAgents']
        
        try:
            for i,j in zip(outboundAgents,inboundAgents):
                network[i][j]['demand'] = 0
        except:
            pass

        # Clear cic % demand edge weights
        try:
            for i,j in zip(outboundAgents,inboundAgents):
                network[i][j]['fractionOfDemandInCIC'] = 0
        except:
            pass


        # Clear utility edge types
        try: 
            for i,j in zip(outboundAgents,inboundAgents):
                network[i][j]['utility'] = 0
        except:
            pass
        
        # Clear cic % spend edge weights
        try:
            for i,j in zip(outboundAgents,inboundAgents):
                network[i][j]['fractionOfActualSpendInCIC'] = 0
        except:
            pass
        # Clear spend edge types
        try: 
            for i,j in zip(outboundAgents,inboundAgents):
                network[i][j]['spend'] = 0
        except:
            pass
    else:
        pass
    x = network
    return (y,x)