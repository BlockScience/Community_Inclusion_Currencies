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
    
    elif maxSpendCurrency[agentToPay] > 0 and maxSpendTokens[agentToPay] > 0:
        if maxSpendTokens[agentToPay] > maxSpendCurrency[agentToPay]:
            spend = maxSpendCurrency[agentToPay]
        elif maxSpendCurrency[agentToPay] > maxSpendTokens[agentToPay]:
            spend = maxSpendTokens[agentToPay]
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

def mint_burn_logic_control(idealCIC,actualCIC,varianceCIC,actualFiat,varianceFiat,idealFiat):
    '''
    Inventory control function to test if the current balance is in an acceptable range. Tolerance range 
    
        Test: mint_burn_logic_control(100000,subset['operatorCICBalance'][499],30000,subset['operatorFiatBalance'][499],30000,100000)
    '''
    if idealFiat - varianceFiat <= actualFiat <= idealFiat + (2*varianceFiat):
        decision = 'none'
        amount = 0
    else:
        if (idealFiat - varianceFiat) > actualFiat:
            decision = 'burn'
            amount = (idealFiat + varianceFiat) - actualFiat
        else:
            pass
        if actualFiat > (idealFiat + varianceFiat):
            decision = 'mint'
            amount = actualFiat - (idealFiat + varianceFiat) 
        else:
            pass

    if decision == 'mint':
        if actualCIC < (idealCIC - varianceCIC):
            if amount > actualCIC:
                decision = 'none'
                amount = 0
            else:
                pass
    if decision == 'none':
        if actualCIC < (idealCIC - varianceCIC):
            decision = 'mint'
            amount = (idealCIC-varianceCIC)
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
    
    
def plot_fan_chart(df,aggregate_dimension,x, y,lx=False,ly=False,density_hack=True):
    def q10(x):
        return x.quantile(0.1)

    def q20(x):
        return x.quantile(0.2)

    def q30(x):
        return x.quantile(0.3)

    def q40(x):
        return x.quantile(0.4)

    def q60(x):
        return x.quantile(0.6)

    def q70(x):
        return x.quantile(0.7)

    def q80(x):
        return x.quantile(0.8)

    def q90(x):
        return x.quantile(0.9)

    run_count = max(df.run)

    agg_metrics = [q10, q20, q30, q40, 'median', q60, q70, q80, q90]
    agg_df = df.groupby(aggregate_dimension).agg({y: agg_metrics})
    agg_metrics = agg_df.columns.levels[1].values
    agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
    plt.figure(figsize=(10,6))

    df = agg_df.reset_index()
    lines = plt.plot(df[x], df[f'{y}_median'])
    color = lines[0].get_color()
    if density_hack:
        avg_iqr = []
        for i in range(len(agg_metrics)-1):
            m = (agg_metrics[i], agg_metrics[i+1])
            iqr = df[f'{y}_{m[1]}'] - df[f'{y}_{m[0]}']
            avg_iqr.append(iqr.sum())
        inv_avg_iqr = [1/i for i in avg_iqr]
        norm_avg_iqr = [i/max(inv_avg_iqr) for i in inv_avg_iqr]
        i = 0
        while i<len(agg_metrics)-1:
            m = (agg_metrics[i], agg_metrics[i+1])
            plt.fill_between(df[x], df[f'{y}_{m[0]}'], df[f'{y}_{m[1]}'], alpha=0.8*norm_avg_iqr[i], facecolor=color, edgecolor=None)
            i += 1
    else:
        i = 0
        while i<len(agg_metrics)/2:
            m = (agg_metrics[i], agg_metrics[-1-i])
            plt.fill_between(df[x], df[f'{y}_{m[0]}'], df[f'{y}_{m[1]}'], alpha=0.3, color=color)
            i += 1

    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Distribution of ' + y + ' over all of ' + str(run_count) + ' Monte Carlo runs'
    plt.title(title_text)
    plt.legend(['Median', 'Interquantile Ranges'])
    if lx:
        plt.xscale('log')
    if ly:
        plt.yscale('log')
        
        
def param_sweep_aggregation(df,aggregation_dimension):
    '''
    Description:
    Function for aggregating parameter sweep runs by mean, median and standard deviation.
    
    Parameters:
    df: pandas dataframe of cadCAD parameter sweep simulation
    aggregation_dimension: dimension to aggregate on, e.x. timestep
    
    Assumptions:
    A cadCAD simulation was completed with an config N > 1 and M.
    
    Returns:
    Lists of parameter subset dataframes for mean, median, and std. The number of dataframes
    in each list is equal to the simulation N.
    
    Example run:
    means,medians,stds = param_sweep_aggregation(result,'timestep')
    '''
    
    df = df[df['substep'] == df.substep.max()]
    subsets = []
    for i in df.subset.unique():
        subsets.append(df[df['subset']==i])

    means = []
    for i in range(0,len(subsets)):
        means.append(subsets[i].groupby(aggregation_dimension).mean().reset_index())

    medians = []
    for i in range(0,len(subsets)):
        medians.append(subsets[i].groupby(aggregation_dimension).median().reset_index())

    stds = []
    for i in range(0,len(subsets)):
        stds.append(subsets[i].groupby(aggregation_dimension).std().reset_index())
        
    return means,medians,stds


def param_plot(dfs,x,y,params,swept,saveFig=False,dims=(10,6)):
    '''
    Description:
    Function to plot parameter sweep monte carlo results to illustrate the effect the swept 
    parameter has on the simulation.
    
    Parameters:
    dfs: list of a pandas dataframes calculated in param_sweep_aggregation()
    x: string of the desired x in the simulation; e.x. 'timestep'
    y: string of the desired x in the simulation; e.x. 'Velocity'
    params: list of parameter sweep values to analyze, e.x. [30,60,90]
    swept: string of the parameter swept, e.e. 'money drip'
    saveFig: optional boolean if the plot should be saved or not
    dims: optional figure size values
    
    Assumptions:
    A cadCAD simulation was completed with an config N > 1 and M and param_sweep_aggregation() was run
    
    Returns:
    Plot
    
    Example run:
    param_plot(medians,'timestep','AggregatedAgentSpend',params,swept)  
    
    '''
    plt.figure(figsize=dims)
    for i in range(0,len(dfs)):
        dfs[i][y].plot()

    plt.legend(params)
    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Effect of ' + swept + ' Parameter Sweep on ' + y
    plt.title(title_text)
    if saveFig:
        plt.savefig(title_text + '_.png')