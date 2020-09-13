from .parts.exogenousProcesses import *
from .parts.kpis import *
from .parts.system import *
from .parts.operatorentity import *

partial_state_update_block = {
    # Exogenous
    'Exogenous': {
        'policies': {
        },
        'variables': {
            'startingBalance': startingBalance,
            '30_day_spend': update_30_day_spend,
            'network': clear_agent_activity,
        }
    },
    'drip': {
        'policies': {
            'action': calculate_drip,
        },
        'variables': {
            'operatorFiatBalance': redCrossDrop,
            'drip': update_drip
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
            'inboundAgents': update_inboundAgents
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
            'network': update_network_withraw,
            'operatorFiatBalance': update_operatorFiatBalance_withdraw,
            'operatorCICBalance': update_operatorCICBalance_withdraw
        }
    },
    # Operator
    'Fees': {
        'policies': {
            'action': fee_calculation
        },
        'variables': {
            'exitFeeRevenue': update_exit_fee_revenue,
            'operatorCICBalance': update_operator_balance_with_fee,
            'withdraw': deduct_fee_from_withdrawal
        }

    },
    'Operator Disburse to Agents': {
        'policies': {
            'action': disbursement_to_agents
        },
        'variables': {
            'network': update_agent_tokens,
            'operatorCICBalance': update_operator_FromDisbursements,
            'totalDistributedToAgents': update_totalDistributedToAgents
        }
    },
    'Operator Inventory Control': {
        'policies': {
            'action': inventory_controller
        },
        'variables': {
            'operatorFiatBalance': update_operator_fiatBalance,
            'operatorCICBalance': update_operator_cicBalance,
            'totalMinted': update_totalMinted,
            'totalBurned': update_totalBurned,
            'fundsInProcess': update_fundsInProcess,
            'network': update_network_mintBurn
        }
    },

    # KPIs
    'KPIs': {
        'policies': {
            'action': kpis
        },
        'variables': {
            'KPIDemand': update_KPIDemand,
            'KPISpend': update_KPISpend,
            'KPISpendOverDemand': update_KPISpendOverDemand
        }
    },
    'Velocity': {
        'policies': {
            'action': velocity_of_money
        },
        'variables': {

            'VelocityOfMoney': update_velocity_of_money
        }
    }
}
