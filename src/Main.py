import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Lists of different values
# Levels of changing electric bill
levels = [0, 76, 201, 301, 401, 601, float('inf')]
# March 2023, Electricity bill at different level
old_cost_list = [4.85, 6.63, 6.95, 7.34, 11.51, 13.26]
# April 2024, Electricity bill at different level
new_cost_list = [5.26, 7.20, 7.59, 8.02, 12.67, 14.61]
# Options to calculate from
options = ['Units', 'Old Total Cost', 'New Total Cost']
# Input box's hints' list
options_hint = ['Enter consumed units', 'Enter old total cost', 'Enter new total cost']
# Tree/Table's columns' list
columns = ["Item", "Old Cost", "New Cost"]


# To calculate the maximum amount of kWh for given cost if vat and other charges are excluded
def cal_max_units(energy_cost, cost_list):
    units = 0
    remaining_cost = energy_cost

    for i in range(len(cost_list)):
        cost = (levels[i + 1] - levels[i]) * cost_list[i]
        if remaining_cost >= cost:
            remaining_cost -= cost
            units += levels[i + 1] - levels[i]
        else:
            units += remaining_cost / cost_list[i]
            break

    return units


# Calculate possible maximum kWh electricity for the given cost
def cal_units(total_cost, cost_list):
    # print(total_cost)
    low = 0
    high = cal_max_units(total_cost, cost_list)

    # binary search
    while low <= high:
        mid = (low + high) // 2
        units, energy_cost, vat, rebate, demand_charge, meter_rent, cal_total_cost = cal_cost(mid, cost_list)
        if abs(cal_total_cost - total_cost) < 0.01:
            return units, energy_cost, vat, rebate, demand_charge, meter_rent, cal_total_cost
        elif cal_total_cost < total_cost:
            low = mid + 1
        else:
            high = mid - 1

    return cal_cost(low, cost_list)


# Calculate the possible maximum cost for given consumed kWh
def cal_cost(units, cost_list):
    energy_cost = 0
    for i in range(len(cost_list)):
        if units >= levels[i]:
            energy_cost += (min(units, levels[i + 1]) - levels[i]) * cost_list[i]

    vat = energy_cost * 0.05
    rebate = energy_cost * 0.005
    demand_charge = 42
    meter_rent = 40
    total_cost = energy_cost + vat - rebate + demand_charge + meter_rent

    return units, energy_cost, vat, rebate, demand_charge, meter_rent, total_cost


def update_labels(event, tree, selection, value, increase_label):
    # If any values is not given as input
    if not value or not value.replace('.', '').isdigit():
        messagebox.showwarning("Notice", 'Enter a valid input please')
        return

    # Clear previous data
    for row in tree.get_children():
        tree.delete(row)

    old_units, old_energy_cost, old_vat, old_rebate, old_demand_charge, old_meter_rent, old_total_cost = 0, 0, 0, 0, 0, 0, 0
    new_units, new_energy_cost, new_vat, new_rebate, new_demand_charge, new_meter_rent, new_total_cost = 0, 0, 0, 0, 0, 0, 0

    # perform operations according to user's selected option
    if selection == "Units":
        old_units, old_energy_cost, old_vat, old_rebate, old_demand_charge, old_meter_rent, old_total_cost = cal_cost(float(value),
                                                                                                  old_cost_list)
        new_units, new_energy_cost, new_vat, new_rebate, new_demand_charge, new_meter_rent, new_total_cost = cal_cost(
            float(value), new_cost_list)
    elif selection == "Old Total Cost":
        old_units, old_energy_cost, old_vat, old_rebate, old_demand_charge, old_meter_rent, old_total_cost = cal_units(float(value),
                                                                                                   old_cost_list)
        new_units, new_energy_cost, new_vat, new_rebate, new_demand_charge, new_meter_rent, new_total_cost = cal_cost(
            old_units, new_cost_list)
    elif selection == "New Total Cost":
        new_units, new_energy_cost, new_vat, new_rebate, new_demand_charge, new_meter_rent, new_total_cost = cal_units(
            float(value), new_cost_list)
        old_units, old_energy_cost, old_vat, old_rebate, old_demand_charge, old_meter_rent, old_total_cost = cal_cost(new_units,
                                                                                                  old_cost_list)

    # Insert new data into the treeview
    tree.insert("", "end", values=["Units", f"{round(old_units, 2)} kWh", f"{round(new_units, 2)} kWh"])
    tree.insert("", "end", values=["Energy Cost", f"{round(old_energy_cost, 2)} tk", f"{round(new_energy_cost, 2)} tk"])
    tree.insert("", "end", values=["VAT", f"{round(old_vat, 2)} tk", f"{round(new_vat, 2)} tk"])
    tree.insert("", "end", values=["Rebate", f"{round(old_rebate, 2)} tk", f"{round(new_rebate, 2)} tk"])
    tree.insert("", "end",
                values=["Demand Charge", f"{round(old_demand_charge, 2)} tk", f"{round(new_demand_charge, 2)} tk"])
    tree.insert("", "end", values=["Meter Rent", f"{round(old_meter_rent, 2)} tk", f"{round(new_meter_rent, 2)} tk"])
    tree.insert("", "end", values=["Total Cost", f"{round(old_total_cost, 2)} tk", f"{round(new_total_cost, 2)} tk"])

    # Calculate and display increase percentage
    increase_percentage = ((new_total_cost - old_total_cost) / old_total_cost) * 100 if old_total_cost != 0 else 0
    increase_label.config(text=f"Increase Rate: {round(increase_percentage, 2)}%", font=("Arial", 16, "bold"))


def on_entry_click(entry):
    if any(entry.get() == option_hint for option_hint in options_hint):
        entry.delete(0, tk.END)
        entry.insert(0, '')
        entry.config(fg='black')


def on_focus_out(event, entry, selection):
    if entry.get() == '' or any(entry.get() == option_hint for option_hint in options_hint):
        entry.delete(0, tk.END)
        if selection == options[0]:
            entry.insert(0, options_hint[0])
        elif selection == options[1]:
            entry.insert(0, options_hint[1])
        elif selection == options[2]:
            entry.insert(0, options_hint[2])
        entry.config(fg='grey')


def on_option_change(entry, selection):
    # print("Option changed called!")
    on_focus_out(None, entry, selection)


def main():
    root = tk.Tk()
    root.geometry('800x400')
    root.title('New Electric Bill')

    # Declaration part
    selection_var = tk.StringVar(root)
    value_var = tk.StringVar()
    value_entry = tk.Entry(root, textvariable=value_var, width=50, justify="center", fg='grey')
    selection_menu = tk.OptionMenu(root, selection_var, *options,
                                   command=lambda selected_option: on_option_change(value_entry, selection_var.get()))
    tree = ttk.Treeview(root, columns=columns, show="headings")
    increase_label = tk.Label(root, text="")
    button = tk.Button(root, text="Calculate",
                       command=lambda: update_labels(None, tree, selection_var.get(), value_var.get(), increase_label))

    # Initialization part
    selection_var.set("Units")
    value_entry.insert(0, options_hint[0])
    value_entry.insert(0, '')
    for col in columns:
        tree.heading(col, text=col)

    # Key binding part
    value_entry.bind('<FocusIn>', lambda event: on_entry_click(value_entry))
    value_entry.bind('<FocusOut>', lambda event: on_focus_out(event, value_entry, selection_var.get()))
    root.bind('<Return>', lambda event: update_labels(event, tree, selection_var.get(), value_var.get(), increase_label))

    # Packing part
    selection_menu.pack()
    value_entry.pack()
    tree.pack()
    increase_label.pack()
    button.pack()

    root.mainloop()


if __name__ == '__main__':
    main()
