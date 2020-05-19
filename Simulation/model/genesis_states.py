from .parts.initialization import * 
import pandas as pd

genesis_states = { 
    # initial states of the economy
    'network': create_network(),# networkx market
    'KPIDemand': {},
    'KPISpend': {},
    'KPISpendOverDemand': {},
    'VelocityOfMoney':0,
    'startingBalance': {},
    '30_day_spend': {},
    'withdraw':{},
    'outboundAgents':[],
    'inboundAgents':[],
    'operatorFiatBalance': initialOperatingFiatBalance,
    'operatorCICBalance': S0,
    'fundsInProcess': {'timestep':[],'decision':[],'cic':[],'shilling':[]},
    'totalDistributedToAgents':0,
    'totalMinted':0,
    'totalBurned':0
}

