import pandas as pd
import matplotlib.pyplot as plt
from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_widget
import ipyleaflet as ipyl

df = {"Aar":          [2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2034], 
      "Landøya":     [33  , 35  , 39  , 47   , 42 , 42  , 36  , 35  , 33  , 30  , 28  , 25  ,   17],
      "Torstad":      [-81 , 48  , 26  , 31   , 15 , -7  , -22 , -49 , -42 , -53 , -65 , -65 , -65 ],
      "Solvang":      [27  , 37  , 30  , 31   , 10 , 1   , -25 , -51 , -70 , -82 , -101, -129, -139],
      "Borgen":       [-73 , -57 , -58 , -50  , -39, -36 , -35 , -35 , -37 , -41 , -42 , -44 , -44 ],
      "Risenga":      [165 , 178 , 157 , 146  , 147, 134 , 130 , 133 , 138 , 140 , 142 , 144 , 145 ],
      "Vollen":       [57  , 64  , 59  , 56   , 56 , 56  , 55  , 34  , 13  , 10  , 9   , 6   , 6   ],
      "Hovedgården":  [29  , 26  , 15  , 5    , -9 , -9  , -22 , -26 , -45 , -66 , -79 , -77 , -83 ],
      "Slemmestad":   [33  , 16  , 23  , 44   , 25 , 7   , -11 , -40 , -50 , -50 , -69 , -69 , -86 ],
      "Røyken":       [-8  , -12 , -8  , -9   , -29, -43 , -62 , -74 , -83 , -104, -124, -136, -142],
      "Spikkestad":   [52  , 62  , 58  , 56   , 59 , 62  , 53  , 44  , 34  , 27  , 22  , 11  , 10  ],
      "Sætre":        [44  , 50  , 57  , 58   , 52 , 49  , 43  , 42  , 43  , 41  , 43  , 44  , 45  ],
      "Tofte":        [43  , 39  , 37  , 42   , 44 , 43  , 40  , 34  , 28  , 25  , 25  , 22  , 15  ]}

df = pd.DataFrame(df)
df_copy = df.copy()
overordnet_kapasitet = [i for i in df_copy.iloc[:, 1:].sum(axis = 1)] 
navn = [i for i in df.columns.tolist()[1:]]
gps = {"Navn": navn,
       "N": [59.8608937, 59.8621818, 59.8486877, 59.8487270, 59.8284839, 59.8025170, 59.8025829, 59.7792919, 59.7458294, 59.7387589, 59.7388396, 59.5409922],
       "E": [10.4998746, 10.4781709, 10.4444050, 10.4057807, 10.4378358, 10.4766078, 10.3993582, 10.4860684, 10.3906545, 10.3111976, 10.2493977, 10.5489635]}
gps = pd.DataFrame(gps)
rv_juster = reactive.Value(0)
avstand = {"Sted": navn,
           "Landøya":     [0 , 5 , 8 , 10, 10, 13, 13, 19, 26, 30, 34, 54],
           "Torstad":      [5 , 0 , 6 , 9 , 8 , 13, 5 , 18, 25, 29, 33, 52],
           "Solvang":      [8 , 6 , 0 , 8 , 10, 15, 6 , 21, 27, 31, 35, 54],
           "Borgen":       [10, 9 , 8 , 0 , 7 , 16, 8 , 21, 24, 29, 33, 52],
           "Risenga":      [10, 8 , 10, 7 , 0 , 11, 7 , 16, 20, 24, 29, 48],
           "Vollen":       [13, 13, 15, 16, 11, 0 , 16, 8 , 16, 20, 25, 44],
           "Hovedgården": [13, 5 , 6 , 8 , 7 , 16, 0 , 14, 14, 16, 14, 33],
           "Slemmestad":   [19, 18, 21, 21, 16, 8 , 14, 0 , 16, 18, 23, 42],
           "Røyken":      [26, 25, 27, 24, 20, 16, 14, 16, 0 , 8 , 16, 35],
           "Spikkestad":   [30, 29, 31, 29, 24, 20, 16, 18, 8 , 0 , 18, 37],
           "Sætre":       [34, 33, 35, 33, 29, 25, 14, 23, 16, 18, 0 , 22],
           "Tofte":        [54, 52, 54, 52, 48, 44, 33, 42, 35, 37, 22, 0 ]}
avstand = pd.DataFrame(avstand)

def bhg_plot(kapasitet):
    x = df_copy.iloc[:, 0]
    y_values = df_copy.iloc[:, 1:] ** 2
    y_min = (max(y_values.max()) * 1.10)**.5 * -1
    y_max = (max(y_values.max()) * 1.10)**.5
    fig, ax = plt.subplots()
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(min(df_copy.iloc[:, 0]), max(df_copy.iloc[:, 0]))
    ax.set_xticks(range(min(df.iloc[:, 0]), max(df.iloc[:, 0]) + 1))
    ax.axhline(y = 0, color = "black", linestyle = "-", linewidth = 2)
    for column in y_values.columns:
        ax.plot(x, df_copy[column], label = column)
    ax.grid(True, which = "both", linestyle = "-", linewidth = 0.5)
    ax.set_xlabel("År")
    ax.set_ylabel("Kapasitet")
    ax.set_title(f"Predikert kapasitet per barnehage fra {min(df_copy.iloc[:, 0])} til {max(df_copy.iloc[:, 0])}.")
    fig.subplots_adjust(right = 0.75)
    ax.legend(bbox_to_anchor = (1.05, 1), loc = 'upper left', frameon = False)
    return fig, ax
def bhg_barplot(kapasitet, aar):
    x_values = df_copy.iloc[:, 1:]
    yr = df_copy.iloc[:, 0].tolist().index(aar)
    values = []
    for i in range(len(df_copy.columns[1:])):
        values.append(df_copy.iloc[:, i + 1].tolist())
    single_values = []
    for i in values:
        for j in i:
            single_values.append(j)
    xlim = (round((max([(i**2)**.5 for i in single_values]) / 10)) * 10) * 1.15
    colnames = df_copy.columns[1:][::-1]
    colcolors = []
    for i in x_values.iloc[yr, :]:
        if i > 100:
            colcolors.append("darkgreen")
        elif i < 100 and i >= 25:
            colcolors.append("lightgreen")
        elif i < 25 and i >= 0:
            colcolors.append("orange")
        elif i < 0 and i >= -25:
            colcolors.append("red")
        else:
            colcolors.append("darkred")    
    colcolors = colcolors[::-1]
    fig, ax = plt.subplots()
    hbars = plt.barh(colnames, x_values.iloc[yr, :][::-1], color = colcolors, edgecolor = "black")
    ax.grid(which = "both", linestyle = "--", linewidth = 0.5)
    fig.subplots_adjust(left = 0.20)
    ax.set_xlim(-xlim, xlim)
    ax.axvline(x = 0, color = "black", linestyle = "-", linewidth = 1)
    ax.bar_label(hbars, label_type = "edge", padding = 5)
    ax.set_title(f"Predikert kapasitet per barnehageområde i {aar}.")
    ax.set_xlabel("Kapasitet")
    return fig, ax
def avstander_barplot(avstand, sted):
    steder = avstand.columns[1:].tolist()
    steder = [i.strip() for i in steder]
    avstander = avstand.iloc[steder.index(sted), 1:].tolist()
    farger = []
    for i in avstander:
        if i <= 5:
            farger.append("darkgreen")
        elif i <= 10:
            farger.append("lightgreen")
        elif i <= 15:
            farger.append("yellow")
        elif i <= 20:
            farger.append("red")
        else:
            farger.append("darkred")
    steder, avstander, farger = steder[::-1], avstander[::-1], farger[::-1]
    fig, ax = plt.subplots()
    hbar = plt.barh(steder, avstander, color = farger, edgecolor = "black")
    ax.grid(which = "both", linestyle = "--", linewidth = 0.5)
    ax.set_xlim(0, 70)
    ax.set_xlabel("Kjøreavstand (minutter)")
    ax.set_title(f"Avstand fra {sted}.")
    ax.bar_label(hbar, label_type = "edge", padding = 5)
    return fig, ax
def juster_kapasitet(df_copy, aar, bhg, justering):
        yr = df_copy.iloc[:, 0].tolist().index(aar)
        bhg = df.columns.tolist().index(bhg)
        for i in range(yr, len(df.iloc[:, bhg])):
            df_copy.iloc[i, bhg] = df_copy.iloc[i, bhg] + justering        
        return df_copy
def reset_kapasitet(df_copy):
    for i in range(len(df.columns)):
        df_copy.iloc[:, i] = df.iloc[:, i]
    return df_copy

ui.page_opts(title = "Predikert barnehagekapasitet i ungdomsskoleområdene perioden 2021 til 2034.", fillable = True)
with ui.layout_columns(col_widths = (3, 6, 3)):
    with ui.card():
        with ui.card(height = "175px"):
            with ui.layout_columns(col_widths = (5, 7)):
                ui.input_select(
                label = "Velg år:", 
                choices = df.iloc[:, 0].tolist(),
                id = "aar")
                @render.data_frame
                @reactive.event(input.aar, input.juster, input.nullstill, rv_juster, ignore_none = False)
                def kapasitet():
                    overordnet_kapasitet = [i for i in df_copy.iloc[:, 1:].sum(axis = 1)] 
                    kap = pd.DataFrame({"Overordnet kapasitet:": [overordnet_kapasitet[df_copy.iloc[:, 0].tolist().index(int(input.aar()))]]})
                    if overordnet_kapasitet[df_copy.iloc[:, 0].tolist().index(int(input.aar()))] >= 0:
                        farge = "#90EE90"
                    else:
                        farge = "#FFCCCB"
                    return render.DataGrid(
                        kap,
                        styles = [
                            {
                                "style": {"background-color": farge,
                                          "text-align": "right",
                                          "padding": "7px"}
                             
                             }
                             ],
                        height = "100px",
                        width = "100%", 
                        summary = False          
                    )
            with ui.layout_columns(col_widths = (7, 5)):
                ui.input_select(
                    label = "Velg barnehageområde:",
                    choices = df.columns[1:].tolist(),
                    id = "bhg",
                    selected = df.columns[1]
                )
                ui.input_numeric(
                    label = "Juster kapasitet:",
                    value = 0,
                    id = "justering"
                )
            with ui.layout_columns(col_widths = (6, 6)):
                ui.input_action_button(
                    label = "Juster",
                    id = "juster"
                ) 
                ui.input_action_button(
                    label = "Nullstill",
                    id = "nullstill"
                )
                @reactive.Effect
                @reactive.event(input.juster)
                def kapasitetsjustering():
                    juster_kapasitet(df_copy, int(input.aar()), input.bhg(), input.justering())
                    rv_juster.set(rv_juster() + 1)
                @reactive.Effect
                @reactive.event(input.nullstill)
                def reset():
                    reset_kapasitet(df_copy)
        with ui.card():
            @render.plot
            def plot1():
                try:
                    avstander_barplot(avstand, str(input.bhg()).strip())
                except:
                    avstander_barplot(avstand, avstand.iloc[:, 0].tolist()[0])
    with ui.card():
        with ui.card():
            @render.plot
            @reactive.event(input.juster, input.nullstill, ignore_none = False)
            def plot2():
                bhg_plot(df_copy)
        with ui.card():
            @render.plot
            @reactive.event(input.juster,input.nullstill, input.aar, ignore_none = False)
            def plot3():
                bhg_barplot(df_copy, int(input.aar()))
    with ui.card():
        @render_widget
        @reactive.event(input.juster, input.nullstill, input.aar, input.bhg, ignore_none = False)
        def map():
            m = ipyl.Map(center = [59.7069, 10.4366], zoom = 10)
            colors = []
            index = df_copy.iloc[:, 0].tolist().index(int(input.aar()))
            for i in range(1, len(df.iloc[:, 0].tolist())):
                if df_copy.iloc[index, i] >= 150:
                    colors.append("darkgreen")
                elif df_copy.iloc[index, i] < 150 and df_copy.iloc[index, i] >= 25:
                    colors.append("lightgreen")
                elif df_copy.iloc[index, i] < 25 and df_copy.iloc[index, i] >= 0:
                    colors.append("orange")
                elif df_copy.iloc[index, i] < 0 and df_copy.iloc[index, i] >= -25:
                    colors.append("red")
                else:
                    colors.append("darkred")
            for i in range(len(gps)):
                if gps.iloc[i, 0] == input.bhg():
                    icon = ipyl.AwesomeIcon(name = 'circle', icon_color = "black", marker_color = colors[i])
                else:
                    icon = ipyl.AwesomeIcon(name = 'circle', icon_color = 'white', marker_color  = colors[i])
                m.add_layer(ipyl.Marker(location = [gps.iloc[i, 1], gps.iloc[i, 2]], draggable = False, title = gps.iloc[i, 0], icon = icon))
            return m
