import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as plt

default_kappa= 4
default_exit_tax = .02

#value function for a given state (R,S)
def invariant(R,S,kappa=default_kappa):
    
    return (S**kappa)/R

#given a value function (parameterized by kappa)
#and an invariant coeficient V0
#return Supply S as a function of reserve R
def reserve(S, V0, kappa=default_kappa):
    return (S**kappa)/V0

#given a value function (parameterized by kappa)
#and an invariant coeficient V0
#return Supply S as a function of reserve R
def supply(R, V0, kappa=default_kappa):
    return (V0*R)**(1/kappa)

#given a value function (parameterized by kappa)
#and an invariant coeficient V0
#return a spot price P as a function of reserve R
def spot_price(R, V0, kappa=default_kappa):
    return kappa*R**((kappa-1)/kappa)/V0**(1/kappa)

#for a given state (R,S)
#given a value function (parameterized by kappa)
#and an invariant coeficient V0
#deposit deltaR to Mint deltaS
#with realized price deltaR/deltaS
def mint(deltaR, R,S, V0, kappa=default_kappa):
    deltaS = (V0*(R+deltaR))**(1/kappa)-S
    if deltaS ==0:
        realized_price = spot_price(R+deltaR, V0, kappa)
    else:
        realized_price = deltaR/deltaS
    deltaS = round(deltaS,2)
    return deltaS, realized_price

#for a given state (R,S)
#given a value function (parameterized by kappa)
#and an invariant coeficient V0
#burn deltaS to Withdraw deltaR
#with realized price deltaR/deltaS
def withdraw(deltaS, R,S, V0, kappa=default_kappa):
    deltaR = R-((S-deltaS)**kappa)/V0
    if deltaS ==0:
        realized_price = spot_price(R+deltaR, V0, kappa)
    else:
        realized_price = deltaR/deltaS
    deltaR = round(deltaR,2)
    return deltaR, realized_price



def iterateEdges(network,edgeToIterate):
    '''
    Description:
    Iterate through a network on a weighted edge and return
    two dictionaries: the inflow and outflow for the given agents
    in the format:
    
    {'Agent':amount}
    '''
    outflows = {}
    inflows = {}
    for i,j in network.edges:
        try:
            amount = network[i][j][edgeToIterate]
            if i in outflows:
                outflows[i] = outflows[i] + amount
            else:
                outflows[i] =  amount
            if j in inflows:
                inflows[j] = inflows[j] + amount
            else:
                inflows[j] = amount
        except:
            pass
    return outflows,inflows


def inflowAndOutflowDictionaryMerge(inflow,outflow):
    '''
    Description:
    Merge two dictionaries and return one dictionary with zero floor'''
    
    merged = {}

    inflowsKeys = [k for k,v in inflow.items() if k not in outflow]
    for i in inflowsKeys:
        merged[i] = inflow[i]
    outflowsKeys = [k for k,v in outflow.items() if k not in inflow]
    for i in outflowsKeys:
        merged[i] = outflow[i]
    overlapKeys = [k for k,v in inflow.items() if k in outflow]
    for i in overlapKeys:
        amt = outflow[i] - inflow[i] 
        if amt < 0:
            merged[i] = 0
        else:
            merged[i] = amt
            pass
        
    return merged

        
def spendCalculation(agentToPay,agentToReceive,rankOrderDemand,maxSpendCurrency,maxSpendTokens,cicPercentage):
    '''
    Function to calculate if an agent can pay for demand given token and currency contraints
    '''
    if (rankOrderDemand[agentToReceive] * (1-cicPercentage)) > maxSpendCurrency[agentToPay]:
        verdict_currency = 'No'
    else:
        verdict_currency = 'Enough'
        
    if (rankOrderDemand[agentToReceive] * cicPercentage) > maxSpendTokens[agentToPay]:
        verdict_cic = 'No'
    else:
        verdict_cic = 'Enough'
    
    if verdict_currency == 'Enough'and verdict_cic == 'Enough':
        spend = rankOrderDemand[agentToReceive]
    
    elif maxSpendCurrency[agentToPay] > 0:
        spend = maxSpendCurrency[agentToPay]
    else:
        spend = 0
        
    return spend


def spendCalculationExternal(agentToPay,agentToReceive,rankOrderDemand,maxSpendCurrency):
    '''
    '''
    if rankOrderDemand[agentToReceive] > maxSpendCurrency[agentToPay]:
        verdict_currency = 'No'
    else:
        verdict_currency = 'Enough'
    
    if verdict_currency == 'Enough':
        spend = rankOrderDemand[agentToReceive]
        
    elif maxSpendCurrency[agentToPay] > 0:
        spend = maxSpendCurrency[agentToPay]
    else:
        spend = 0
        
    return spend


def DictionaryMergeAddition(inflow,outflow):
    '''
    Description:
    Merge two dictionaries and return one dictionary'''
    
    merged = {}

    inflowsKeys = [k for k,v in inflow.items() if k not in outflow]
    for i in inflowsKeys:
        merged[i] = inflow[i]
    outflowsKeys = [k for k,v in outflow.items() if k not in inflow]
    for i in outflowsKeys:
        merged[i] = outflow[i]
    overlapKeys = [k for k,v in inflow.items() if k in outflow]
    for i in overlapKeys:
        merged[i] = outflow[i] + inflow[i] 
        
    return merged

def mint_burn_logic_control(ideal,actual,variance,fiat,fiat_variance,ideal_fiat):
    '''
    Inventory control function to test if the current balance is in an acceptable range. Tolerance range 
    '''
    if ideal - variance <= actual <= ideal + (2*variance):
        decision = 'none'
        amount = 0
    else:
        if (ideal + variance) > actual:
            decision = 'mint'
            amount = (ideal + variance) - actual
        else:
            pass
        if actual > (ideal + variance):
            decision = 'burn'
            amount = actual - (ideal + variance) 
        else:
            pass

    if decision == 'mint':
        if fiat < (ideal_fiat - fiat_variance):
            if amount > fiat:
                decision = 'none'
                amount = 0
            else:
                pass
    if decision == 'none':
        if fiat < (ideal_fiat - fiat_variance):
            decision = 'mint'
            amount = (ideal_fiat-fiat_variance)
        else:
            pass
    
    amount = round(amount,2)
    return decision, amount
    
#NetworkX functions
def get_nodes_by_type(g, node_type_selection):
    return [node for node in g.nodes if g.nodes[node]['type']== node_type_selection]

def get_edges_by_type(g, edge_type_selection):
    return [edge for edge in g.edges if g.edges[edge]['type']== edge_type_selection]

def get_edges(g):
    return [edge for edge in g.edges if g.edges[edge]]

def get_nodes(g):
    '''
    df.network.apply(lambda g: np.array([g.nodes[j]['balls'] for j in get_nodes(g)]))
    '''
    return [node for node in g.nodes if g.nodes[node]]

def aggregate_runs(df,aggregate_dimension):
    '''
    Function to aggregate the monte carlo runs along a single dimension.
    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    Example run:
    mean_df,median_df,std_df,min_df = aggregate_runs(df,'timestep')
    '''
    df = df[df['substep'] == df.substep.max()]
    mean_df = df.groupby(aggregate_dimension).mean().reset_index()
    median_df = df.groupby(aggregate_dimension).median().reset_index()
    std_df = df.groupby(aggregate_dimension).std().reset_index()
    min_df = df.groupby(aggregate_dimension).min().reset_index()

    return mean_df,median_df,std_df,min_df



def plot_averaged_runs(df,aggregate_dimension,x, y,run_count,lx=False,ly=False, suppMin=False):
    '''
    Function to plot the mean, median, etc of the monte carlo runs along a single variable.
    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting
    run_count = the number of monte carlo simulations
    lx = True/False for if the x axis should be logged
    ly = True/False for if the x axis should be logged
    suppMin: True/False for if the miniumum value should be plotted
    Note: Run aggregate_runs before using this function
    Example run:
    '''
    mean_df,median_df,std_df,min_df = aggregate_runs(df,aggregate_dimension)

    plt.figure(figsize=(10,6))
    if not(suppMin):
        plt.plot(mean_df[x].values, mean_df[y].values,
             mean_df[x].values,median_df[y].values,
             mean_df[x].values,mean_df[y].values+std_df[y].values,
             mean_df[x].values,min_df[y].values)
        plt.legend(['mean', 'median', 'mean+ 1*std', 'min'],bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    else:
        plt.plot(mean_df[x].values, mean_df[y].values,
             mean_df[x].values,median_df[y].values,
             mean_df[x].values,mean_df[y].values+std_df[y].values,
             mean_df[x].values,mean_df[y].values-std_df[y].values)
        plt.legend(['mean', 'median', 'mean+ 1*std', 'mean - 1*std'],bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Performance of ' + y + ' over all of ' + str(run_count) + ' Monte Carlo runs'
    plt.title(title_text)
    if lx:
        plt.xscale('log')

    if ly:
        plt.yscale('log')

def plot_median_with_quantiles(df,aggregate_dimension,x, y):
    '''
    Function to plot the median and 1st and 3rd quartiles of the monte carlo runs along a single variable.
    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting

    Example run:
    plot_median_with_quantiles(df,'timestep','timestep','AggregatedAgentSpend')
    '''
    
    df = df[df['substep'] == df.substep.max()]
    firstQuantile = df.groupby(aggregate_dimension).quantile(0.25).reset_index()
    thirdQuantile = df.groupby(aggregate_dimension).quantile(0.75).reset_index()
    median_df = df.groupby(aggregate_dimension).median().reset_index()
    
    fig, ax = plt.subplots(1,figsize=(10,6))
    ax.plot(median_df[x].values, median_df[y].values, lw=2, label='Median', color='blue')
    ax.fill_between(firstQuantile[x].values, firstQuantile[y].values, thirdQuantile[y].values, facecolor='black', alpha=0.2)
    ax.set_title(y + ' Median')
    ax.legend(loc='upper left')
    ax.set_xlabel('Timestep')
    ax.set_ylabel('Amount')
    ax.grid()
    
def plot_median_with_quantiles_annotation(df,aggregate_dimension,x, y):
    '''
    Function to plot the median and 1st and 3rd quartiles of the monte carlo runs along a single variable.
    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting

    Example run:
    plot_median_with_quantiles(df,'timestep','timestep','AggregatedAgentSpend')
    '''
    
    df = df[df['substep'] == df.substep.max()]
    firstQuantile = df.groupby(aggregate_dimension).quantile(0.25).reset_index()
    thirdQuantile = df.groupby(aggregate_dimension).quantile(0.75).reset_index()
    median_df = df.groupby(aggregate_dimension).median().reset_index()
    
    fig, ax = plt.subplots(1,figsize=(10,6))
    ax.axvline(x=30,linewidth=2, color='r')
    ax.annotate('Agents can withdraw and Red Cross Drip occurs', xy=(30,2), xytext=(35, 1),
            arrowprops=dict(facecolor='black', shrink=0.05))
    
    ax.axvline(x=60,linewidth=2, color='r')
    ax.axvline(x=90,linewidth=2, color='r')
    ax.plot(median_df[x].values, median_df[y].values, lw=2, label='Median', color='blue')
    ax.fill_between(firstQuantile[x].values, firstQuantile[y].values, thirdQuantile[y].values, facecolor='black', alpha=0.2)
    ax.set_title(y + ' Median')
    ax.legend(loc='upper left')
    ax.set_xlabel('Timestep')
    ax.set_ylabel('Amount')
    ax.grid()


def first_five_plot(df,aggregate_dimension,x,y,run_count):
    '''
    A function that generates timeseries plot of at most the first five Monte Carlo runs.
    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting
    run_count = the number of monte carlo simulations
    Note: Run aggregate_runs before using this function
    Example run:
    first_five_plot(df,'timestep','timestep','revenue',run_count=100)
    '''
    mean_df,median_df,std_df,min_df = aggregate_runs(df,aggregate_dimension)
    plt.figure(figsize=(10,6))
    if run_count < 5:
        runs = run_count
    else:
        runs = 5
    for r in range(1,runs+1):
        legend_name = 'Run ' + str(r)
        plt.plot(df[df.run==r].timestep, df[df.run==r][y], label = legend_name )
    plt.plot(mean_df[x], mean_df[y], label = 'Mean', color = 'black')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Performance of ' + y + ' over the First ' + str(runs) + ' Monte Carlo Runs'
    plt.title(title_text)
    plt.savefig(y +'_FirstFiveRuns.jpeg')