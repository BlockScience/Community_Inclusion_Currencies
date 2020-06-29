from Simulation_param.model.parts.exogenousProcesses import *
from Simulation_param.model.parts.kpis import *
from Simulation_param.model.parts.system import *
from Simulation_param.model.parts.operatorentity import *

partial_state_update_block = {
    # Exogenous
    'Exogenous': {
        'policies': {
        },
        'variables': {
            'startingBalance': startingBalance,
            'operatorFiatBalance': redCrossDrop,
            '30_day_spend': update_30_day_spend,
            'network':clear_agent_activity
        }
    },
    # Users
    'Behaviors': {
        'policies': {
            'action': choose_agents
        },
        'variables': {
        'network': update_agent_activity,
        'outboundAgents': update_outboundAgents,
        'inboundAgents':update_inboundAgents
        }
    },
    'Spend allocation': {
        'policies': {
            'action': spend_allocation
        },
        'variables': {
        'network': update_node_spend
        }
    },
    'Withdraw behavior': {
        'policies': {
            'action': withdraw_calculation
        },
        'variables': {
        'withdraw': update_withdraw,
        'network':update_network_withraw,
        'operatorFiatBalance':update_operatorFiatBalance_withdraw,
        'operatorCICBalance':update_operatorCICBalance_withdraw
        }
    },
    # Operator
    'Operator Disburse to Agents': {
        'policies': {
            'action': disbursement_to_agents
        },
        'variables': {
        'network':update_agent_tokens,
        'operatorCICBalance':update_operator_FromDisbursements,
        'totalDistributedToAgents':update_totalDistributedToAgents
        }
    },
    'Operator Inventory Control': {
        'policies': {
            'action': inventory_controller
        },
        'variables': {
        'operatorFiatBalance':update_operator_fiatBalance,
        'operatorCICBalance':update_operator_cicBalance, 
        'totalMinted': update_totalMinted,
        'totalBurned':update_totalBurned,
        'fundsInProcess':update_fundsInProcess,
        'network':update_network_mintBurn
        }
    },
    
    # KPIs
    'KPIs': {
        'policies': {
            'action':kpis
        },
        'variables':{
            'KPIDemand': update_KPIDemand,
            'KPISpend': update_KPISpend,
            'KPISpendOverDemand': update_KPISpendOverDemand        
        }
    },
    'Velocity': {
        'policies': {
            'action':velocity_of_money
        },
        'variables':{

            'VelocityOfMoney': update_velocity_of_money
        }
    }
}
