from gym_jobshop.envs.src import environment, global_settings
import csv


def measure_cost():
    """
    Logic for measuring costs:
    Once at the end of every period (after orders have been released, processed and shipped) we update the cost.
    The cost that incurred in the past period will be added to the sum of the respective cost (e.g. we
        add all cost from FGI inventories from the past period to the sum of all FGI costs and so on)
    The cost is calculated by multiplying a given cost factor (see global_settings.py) with the amount of orders
    in the respective inventory (e.g. we have 5 orders in FGI and the cost factor is 4, then the cost for that period
    is 20)
    :return: return nothing
    """
    ################### Measure cost for shopfloor (machines + WIP inventories):
    for wip in environment.list_of_all_wip_elements:
        global_settings.sum_shopfloor_cost += len(wip) * global_settings.cost_per_item_in_shopfloor
    for machine in environment.list_of_all_machines:
        if len(machine.orders_inside_the_machine) > 0:
            global_settings.sum_shopfloor_cost += len(machine.orders_inside_the_machine) * \
                                                  global_settings.cost_per_item_in_shopfloor
    ################### Measure cost for finished goods inventory:
    global_settings.sum_fgi_cost += len(environment.finished_goods_inventory) * global_settings.cost_per_item_in_fgi
    ################### Measure cost for late goods (= backorder cost) in the last step of simulation:
    if global_settings.current_time == global_settings.maximum_simulation_duration - 1:
        # for every order in shipped_orders, add its lateness to the sum of all lateness
        for order_element in environment.shipped_orders:
            global_settings.sum_lateness_cost += order_element.lateness * global_settings.cost_per_late_item
    ################### Measure total cost:
    global_settings.total_cost = global_settings.sum_shopfloor_cost + global_settings.sum_fgi_cost \
                                 + global_settings.sum_lateness_cost
    return


def measure_lateness():
    return


def reset_all_costs():
    global_settings.total_cost = 0
    global_settings.sum_shopfloor_cost = 0
    global_settings.sum_fgi_cost = 0
    global_settings.sum_lateness_cost = 0
    return


def utilization_per_step(): # this appends to the steps.csv file
    amount_of_active_machines = 0
    for machine in environment.list_of_all_machines:
        if len(machine.orders_inside_the_machine) > 0:
            amount_of_active_machines += 1
    utilization = amount_of_active_machines / 6
    # Append results to CSV file
    with open('../steps.csv', mode='a') as steps_CSV:
        results_writer = csv.writer(steps_CSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow([global_settings.current_time,
                                 len(environment.wip_A), len(environment.wip_B), len(environment.wip_C),
                                 len(environment.wip_D),
                                 len(environment.wip_E), len(environment.wip_F),
                                 len(environment.machine_A.orders_inside_the_machine),
                                 len(environment.machine_B.orders_inside_the_machine),
                                 len(environment.machine_C.orders_inside_the_machine),
                                 len(environment.machine_D.orders_inside_the_machine),
                                 len(environment.machine_E.orders_inside_the_machine),
                                 len(environment.machine_F.orders_inside_the_machine), utilization
                                 ])
        steps_CSV.close()
    return


def measure_order_flow_times():
    list_of_earliness_per_order = []
    list_of_flow_time_per_order = []
    # Create CSV file to store results after each iteration
    with open('../orders_' + str(global_settings.random_seed) + '.csv', mode='w') as orders_CSV:
        results_writer = csv.writer(orders_CSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['OrderID', 'product_type', 'creation_date', 'order_release_date',
                                 'arrival_m1', 'arrival_wip_step2', 'arrival_m_step_2',
                                 'arrival_wip_step_3', 'arrival_m_step_3', 'finished_production_date',
                                 'due_date', 'shipping_date', 'lateness', 'earliness', 'flow_time'])
        for order_element in environment.shipped_orders:
            order_element.arrvival_m1 = order_element.arrival_times_m1m2m3[0]
            order_element.arrival_prodstep_2_m = order_element.arrival_times_m1m2m3[1]
            order_element.arrival_prodstep_3_m = order_element.arrival_times_m1m2m3[2]
            results_writer.writerow([
                order_element.orderID, order_element.product_type,
                order_element.creation_date,order_element.order_release_date,
                order_element.arrvival_m1, order_element.arrival_prodstep_2_wip,
                order_element.arrival_prodstep_2_m, order_element.arrival_prodstep_3_wip,
                order_element.arrival_prodstep_3_m,
                order_element.finished_production_date, order_element.due_date,
                order_element.shipping_date,order_element.lateness,
                order_element.earliness, order_element.flow_time
            ])
            list_of_earliness_per_order.append(order_element.earliness)
            list_of_flow_time_per_order.append(order_element.flow_time)

        # Append average results to the end of the CSV
        # global_settings.average_earliness_of_all_orders = statistics.mean(list_of_earliness_per_order)
        # global_settings.average_flow_time_of_all_orders = statistics.mean(list_of_flow_time_per_order)
        # results_writer.writerow(['avg_earliness','avg_lateness', 'avg_flow_time'])
        # results_writer.writerow([global_settings.average_earliness_of_all_orders,'avg_lateness', global_settings.average_flow_time_of_all_orders])
        orders_CSV.close()
    return



