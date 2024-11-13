import copy
from datetime import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_widget
import ipyleaflet as ipyl
from colorwheel import ColorWheel

df = {"Aar":          [2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2034], 
      "Landøya":      [33  , 35  , 39  , 47   , 42 , 42  , 36  , 35  , 33  , 30  , 28  , 25  ,   17],
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

avstand = {"Sted": navn,
           "Landøya":      [0 , 5 , 8 , 10, 10, 13, 13, 19, 26, 30, 34, 54],
           "Torstad":      [5 , 0 , 6 , 9 , 8 , 13, 5 , 18, 25, 29, 33, 52],
           "Solvang":      [8 , 6 , 0 , 8 , 10, 15, 6 , 21, 27, 31, 35, 54],
           "Borgen":       [10, 9 , 8 , 0 , 7 , 16, 8 , 21, 24, 29, 33, 52],
           "Risenga":      [10, 8 , 10, 7 , 0 , 11, 7 , 16, 20, 24, 29, 48],
           "Vollen":       [13, 13, 15, 16, 11, 0 , 16, 8 , 16, 20, 25, 44],
           "Hovedgården":  [13, 5 , 6 , 8 , 7 , 16, 0 , 14, 14, 16, 14, 33],
           "Slemmestad":   [19, 18, 21, 21, 16, 8 , 14, 0 , 16, 18, 23, 42],
           "Røyken":       [26, 25, 27, 24, 20, 16, 14, 16, 0 , 8 , 16, 35],
           "Spikkestad":   [30, 29, 31, 29, 24, 20, 16, 18, 8 , 0 , 18, 37],
           "Sætre":        [34, 33, 35, 33, 29, 25, 14, 23, 16, 18, 0 , 22],
           "Tofte":        [54, 52, 54, 52, 48, 44, 33, 42, 35, 37, 22, 0 ]}

avstand = pd.DataFrame(avstand)

# INITIAL REACTIVE VALUES
rv_juster = reactive.Value(0)
rv_tilbake = reactive.Value(0)
rv_nullstill = reactive.Value(0)

justeringslog = []
justeringslog_backup = []
justeringshistorikk = pd.DataFrame(columns = ["År", "Område", "Justering", "Ny kapasitet", "Kommentar"])
justeringshistorikk_backup = pd.DataFrame(columns = ["År", "Område", "Justering", "Ny kapasitet", "Kommentar"])

df_backup = None
nullstill = 0

if len(df_copy.columns[1:]) <= 6:
    lc = ColorWheel(color_number = 6).colors
elif len(df_copy.columns[1:]) <= 12:
    lc = ColorWheel(color_number = 12).colors
else:
    lc = ColorWheel(color_number = ((len(df_copy.columns[1:]) // 12) + 1) * 12).colors
lc = [(i[0] / 255, i[1] / 255, i[2] / 255) for i in lc]
def bhg_plot(bhg):
    x = df_copy.iloc[:, 0]
    y_values = df_copy.iloc[:, 1:] ** 2
    y_min = (max(y_values.max()) * 1.10)**.5 * -1
    y_max = (max(y_values.max()) * 1.10)**.5
    bhgs = df_copy.columns[1:]
    ncol = range(len(bhgs))
    fig1, ax1 = plt.subplots()
    ax1.grid(True, which = "both", linestyle = "-", linewidth = 0.5)
    ax1.axhline(y = 0, color = "black", linestyle = "-", linewidth = 1)
    opacities = [1 if bhgs[i] == bhg else 0.1 for i in ncol]
    [ax1.plot(x, df_copy[bhgs[i]], label = bhgs[i], linewidth = 2, alpha = opacities[i], color = lc[i]) for i in ncol]
    ax1.set_ylim(y_min, y_max)
    ax1.set_xlim(min(df_copy.iloc[:, 0]), max(df_copy.iloc[:, 0]))
    ax1.set_xticks(range(min(df.iloc[:, 0]), max(df.iloc[:, 0]) + 1))
    ax1.set_xlabel("År")
    ax1.set_ylabel("Kapasitet")
    ax1.set_title(f"Forventet kapasitet per barnehageområde fra {min(df_copy.iloc[:, 0])} til {max(df_copy.iloc[:, 0])}.")
    ax1.legend(bbox_to_anchor = (1.05, 1), loc = 'upper left', frameon = False)
    return fig1, ax1

def overordnet_kapasitet_plot():
    y_values = [i for i in df_copy.iloc[:, 1:].sum(axis = 1)]
    x_values = [str(i) for i in df_copy.iloc[:, 0]]
    maxvalue = max([(i**2)**.5 for i in y_values])
    colcolors = ["darkgreen" if i > 300 else
                 "lightgreen" if 100 <= i <= 300 else
                 "orange" if 0 <= i < 100 else
                 "red" if -100 <= i < 0 else
                 "darkred" for i in y_values]
    fig2, ax2 = plt.subplots()
    bars2 = plt.bar(x_values, y_values, color = colcolors, edgecolor = "black")
    ax2.grid(which = "both", linestyle = "--", linewidth = 0.5)
    ax2.set_ylim(-maxvalue * 1.3, maxvalue * 1.3)
    ax2.axhline(y = 0, color = "black", linestyle = "-", linewidth = 1)
    ax2.set_title(f"Forventet overordnet kapasitet i Asker fra {min(df_copy.iloc[:, 0])} til {max(df_copy.iloc[:, 0])}.")
    ax2.bar_label(bars2, label_type = "edge", padding = 5)
    return fig2, ax2

def bhg_barplot(aar):
    x_values = df_copy.iloc[:, 1:]
    yr = df_copy.iloc[:, 0].tolist().index(aar)
    values = [df_copy.iloc[:, i + 1].tolist() for i in range(len(df_copy.columns[1:]))]
    single_values = [j for i in values for j in i]
    xlim = (round((max([(i**2)**.5 for i in single_values]) / 10)) * 10) * 1.4
    colnames = df_copy.columns[1:][::-1]
    colcolors = [
        "darkgreen" if i > 100 else
        "lightgreen" if 25 <= i <= 100 else
        "orange" if 0 <= i < 25 else
        "red" if -25 <= i < 0 else
        "darkred" for i in x_values.iloc[yr, :]]
    colcolors = colcolors[::-1]
    fig3, ax3 = plt.subplots(gridspec_kw = {"left": .3, "bottom": .15})
    bars3 = plt.barh(colnames, x_values.iloc[yr, :][::-1], color = colcolors, edgecolor = "black")
    plt.xticks([-200, -100, 0, 100, 200]) #TODO: Autojuster
    ax3.grid(which = "both", linestyle = "--", linewidth = 0.5)
    ax3.set_xlim(-xlim, xlim)
    ax3.axvline(x = 0, color = "black", linestyle = "-", linewidth = 1)
    ax3.set_title(f"Forventede for {aar}.")
    ax3.set_xlabel("Kapasitet")
    ax3.bar_label(bars3, label_type = "edge", padding = 5)
    return fig3, ax3

def bhg_barplot_2(bhg):
    x_values = df_copy.iloc[:, 1:]
    values = [df_copy.iloc[:, i + 1].tolist() for i in range(len(df_copy.columns[1:]))]
    single_values = [j for i in values for j in i]
    xlim = (round((max([(i**2)**.5 for i in single_values]) / 10)) * 10) * 1.4
    x_values = x_values[bhg]
    colnames = [str(i) for i in df_copy.iloc[:, 0]]
    colcolors = ["darkgreen" if i > 100 else
                 "lightgreen" if 25 <= i <= 100 else
                 "orange" if 0 <= i < 25 else
                 "red" if -25 <= i < 0 else
                 "darkred" for i in x_values]
    colcolors = colcolors[::-1]
    fig4, ax4 = plt.subplots(gridspec_kw = {"left": .3, "bottom": .15})
    bars4 = plt.barh(colnames, x_values, color = colcolors, edgecolor = "black")
    plt.xticks([-200, -100, 0, 100, 200]) #TODO: Autojuster
    ax4.grid(which = "both", linestyle = "--", linewidth = 0.5)
    ax4.set_xlim(-xlim, xlim)
    ax4.axvline(x = 0 , color = "black", linestyle = "-", linewidth = 1)
    ax4.set_title(f"Forventede for {bhg}.")
    ax4.set_xlabel("Kapasitet")
    ax4.set_title(f"Forventede for {bhg}.")    
    ax4.bar_label(bars4, label_type = "edge", padding = 5)
    return fig4, ax4

fig5, ax5 = None, None
bars5 = None
def avstander_barplot(avstand, sted):
    steder = avstand.columns[1:].tolist()
    steder = [i.strip() for i in steder]
    avstander = avstand.iloc[steder.index(sted), 1:].tolist()
    farger = ["darkgreen" if i <= 5 else
              "lightgreen" if i <= 10 else
              "yellow" if i <= 15 else
              "red" if i <= 20 else
              "darkred" for i in avstander]
    steder, avstander, farger = steder[::-1], avstander[::-1], farger[::-1]
    fig, ax = plt.subplots()
    hbar = plt.barh(steder, avstander, color = farger, edgecolor = "black")
    ax.grid(which = "both", linestyle = "--", linewidth = 0.5)
    ax.set_xlim(0, 70)
    ax.set_xlabel("Kjøreavstand (minutter)")
    ax.set_title(f"Avstander fra {sted}.")
    ax.bar_label(hbar, label_type = "edge", padding = 5)
    return fig, ax

def draw_map():
    m = ipyl.Map(center = [59.7069, 10.4366], zoom = 9, scroll_wheel_zoom = True)
    index = df_copy.iloc[:, 0].tolist().index(int(input.aar()))
    colors = ["darkgreen" if df_copy.iloc[index, i] >= 150 else
              "lightgreen" if df_copy.iloc[index, i] < 150 and df_copy.iloc[index, i] >= 25 else
              "orange" if df_copy.iloc[index, i] < 25 and df_copy.iloc[index, i] >= 0 else
              "red" if df_copy.iloc[index, i] < 0 and df_copy.iloc[index, i] >= -25 else
              "darkred" for i in range(1, len(df.iloc[:, 0].tolist()))]
    icon_color = ["white" if gps.iloc[i, 0] != input.bhg() else "black" for i in range(len(gps))]
    icons = [ipyl.AwesomeIcon(name = "circle", icon_color = icon_color[i], marker_color  = colors[i]) for i in range(len(gps))]
    [m.add_layer(ipyl.Marker(location = [gps.iloc[i, 1], gps.iloc[i, 2]], draggable = False, title = gps.iloc[i, 0], icon = icons[i])) for i in range(len(gps))]
    return m

def juster_kapasitet(aar, bhg, justering, kommentar):
    global nullstill, df_copy, justeringshistorikk
    yr = df_copy.iloc[:, 0].tolist().index(aar)
    bhg = df.columns.tolist().index(bhg)
    for i in range(yr, len(df.iloc[:, bhg])):
        df_copy.iloc[i, bhg] = df_copy.iloc[i, bhg] + justering
    kapasitet_ = df_copy.iloc[yr, bhg]
    justeringslog.append([yr, bhg, justering, int(kapasitet_), kommentar])
    justeringshistorikk.loc[justeringshistorikk.shape[0]] = [input.aar(), input.bhg(), justering, int(kapasitet_), kommentar]
    nullstill = 0

def reset_kapasitet():
    global justeringslog_backup, justeringshistorikk, justeringshistorikk_backup, nullstill, df_backup, df_copy
    justeringshistorikk_backup = justeringshistorikk.copy(deep = True)
    justeringshistorikk = pd.DataFrame(columns = ["År", "Område", "Justering", "Ny kapasitet", "Kommentar"])
    df_backup = df_copy.copy(deep = True)
    justeringslog_backup = copy.deepcopy(justeringslog)
    for i in range(len(df.columns.to_list())):
        df_copy.iloc[:, i] = df.iloc[:, i]
    nullstill = 1

def tilbakestill_kapasitet():
    global nullstill, justeringslog, justeringshistorikk, df_copy
    if nullstill == 1:
        justeringslog = copy.deepcopy(justeringslog_backup)
        justeringshistorikk = justeringshistorikk_backup.copy(deep = True)
        nullstill = 0
        df_copy = df_backup.copy(deep = True)
        nullstill = 0
        return df_copy
    if len(justeringslog) == 0:
        return None
    yr = justeringslog[len(justeringslog) - 1][0]
    bhg = justeringslog[len(justeringslog) - 1][1]
    for i in range(yr, len(df.iloc[:, bhg])):
        df_copy.iloc[i, bhg] = df_copy.iloc[i, bhg] - justeringslog[len(justeringslog) - 1][2]
    justeringslog.pop(len(justeringslog) - 1)
    nullstill = 0
    return df_copy
    
def opplastet_log():
    global justeringslog, df_copy, justeringshistorikk
    df_copy.iloc[:, :] = df.iloc[:, :].copy()
    justeringshistorikk = pd.read_csv(input.last_opp()[0]["datapath"])
    justeringslog = justeringshistorikk.values.tolist()        
    for i in justeringshistorikk.values:
        rowindex = df_copy.iloc[:, 0].tolist().index(i[0])
        colindex = df_copy.columns.tolist().index(i[1])
        df_copy.iloc[rowindex:, colindex] = [j + i[2] for j in df_copy.iloc[rowindex:, colindex]]

ui.page_opts(title = ui.HTML(
    """
    <img src = 'https://www.asker.kommune.no/contentassets/21d3166cd6d745eab948cf480d345d1b/logopolitical.svg' style = 'height:50px; margin-right:50px; float:left; vertical-align:middle;'>
    <span style = 'font-weight:bold; vertical-align: middle;'> Analyseverktøy for justering av barnehagekapasitet i ungdomsskoleområdene perioden 2021 til 2034.</span>
    """), 
    window_title = "Forventet barnehagekapasitet i ungdomsskoleområdene perioden 2021 til 2034.", 
    fillable = True, style = "background-color: lightblue;")

with ui.layout_columns(col_widths = (3, 6, 3), gap = "0.5%"):
    with ui.card():
        with ui.card(class_ = "border-0", height = "50%"):
            with ui.layout_columns(col_widths = (4, 8), fill = True):

                ui.input_select(
                    label = "Velg år:", 
                    choices = df.iloc[:, 0].tolist(),
                    id = "aar")
                
                @render.data_frame
                @reactive.event(input.aar, input.juster, input.tilbake, input.nullstill, rv_juster, rv_tilbake, rv_nullstill, ignore_none = False)
                def kapasitet():
                    overordnet_kapasitet = [i for i in df_copy.iloc[:, 1:].sum(axis = 1)] 
                    kap = pd.DataFrame({f"Overordnet kapasitet i {input.aar()}:": [overordnet_kapasitet[df_copy.iloc[:, 0].tolist().index(int(input.aar()))]]}, dtype = str)
                    if int(kap.iloc[0, 0]) > 0:
                        kap.iloc[0, 0] = "+" + kap.iloc[0, 0]
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
                
            with ui.layout_columns(col_widths = (12)):
                ui.input_text_area(
                    label = "Kommentar:",
                    value = "",
                    id = "kommentar",
                    width = "100%"
                )
            
            with ui.layout_columns(col_widths = (4, 4, 4)):
                ui.input_action_button(
                    class_ = "btn-success",
                    label = "Juster",
                    id = "juster"
                ) 
                ui.input_action_button(
                    class_ = "btn-warning",
                    label = "Angre",
                    id = "tilbake"
                )
                ui.input_action_button(
                    class_ = "btn-danger",
                    label = "Reset",
                    id = "nullstill"
                )
                
                @reactive.Effect
                @reactive.event(input.juster)
                def kapasitetsjustering():
                    juster_kapasitet(int(input.aar()), input.bhg(), input.justering(), input.kommentar())
                    rv_juster.set(rv_juster() + 1)
                
                @reactive.Effect
                @reactive.event(input.tilbake)
                def tilbakestill():
                    tilbakestill_kapasitet()
                    rv_tilbake.set(rv_tilbake() + 1)
                
                @reactive.Effect
                @reactive.event(input.nullstill)
                def reset():
                    reset_kapasitet()
                    justeringslog.clear()
                    rv_nullstill.set(rv_nullstill() + 1)

        with ui.navset_card_tab(id = "bhg_kapasiteter"):
            with ui.nav_panel(f"Kapasiteter for år"):
                @render.plot
                @reactive.event(input.juster, input.tilbake, input.nullstill, input.aar, ignore_none = False)
                def plot1_1():
                    bhg_barplot(int(input.aar()))
            with ui.nav_panel(f"Kapasiteter for området"):
                @render.plot
                @reactive.event(input.juster, input.tilbake, input.nullstill, input.bhg, ignore_none = False)
                def plot1_2():
                    bhg_barplot_2(input.bhg())
    
    with ui.card(fillable = True):
        with ui.layout_columns(col_widths = (12), row_heights = ("48.5%", "48.5%")):
            with ui.navset_card_tab(id = "justeringslogg"):
                with ui.nav_panel("Justeringslogg"):
                    with ui.layout_columns(col_widths = (12), row_heights = ("7.5%", "87.5%")):               
                        with ui.layout_columns(col_widths = (9, 3), row_heights = ("100%")): 
                            ui.input_file(id = "last_opp", button_label = "Last opp", label = "", width = "100%", 
                                          placeholder = "Velg .csv fil med justeringslogg", accept = [".csv"], multiple = False)
                            
                            @reactive.effect
                            @reactive.event(input.last_opp)
                            def log_opplastet():
                                opplastet_log()

                            @render.download(filename = f"justeringslogg {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.csv", media_type = "text/csv", label = "Last ned")
                            def last_ned():
                                path = os.path.join("justeringslogg.csv")
                                return path

                        with ui.layout_columns(col_widths = (12), row_heights = "100%"):
                            @render.data_frame
                            @reactive.event(input.juster, input.tilbake, input.nullstill, input.last_opp, ignore_none = False)
                            def kapasitet_tabell():
                                return render.DataGrid(justeringshistorikk, width = "100%")

            with ui.navset_card_tab(id = "Kapasitetplots"): 
                with ui.nav_panel("Per barnehageområde"):
                    @render.plot
                    @reactive.event(input.juster, input.tilbake, input.nullstill, input.bhg, ignore_none = False)
                    def plot2_1():
                        bhg_plot(input.bhg())

                with ui.nav_panel("Overordnet for Asker"):
                    @render.plot
                    @reactive.event(input.juster, input.tilbake, input.nullstill, input.bhg, ignore_none = False)
                    def plot2_2():
                        overordnet_kapasitet_plot()

    with ui.card():
        with ui.card():
            @render.plot
            def plot3_1():
                try:
                    avstander_barplot(avstand, str(input.bhg()).strip())
                except:
                    avstander_barplot(avstand, avstand.iloc[:, 0].tolist()[0])
        
        with ui.card():
            @render_widget
            @reactive.event(input.juster, input.tilbake, input.nullstill, input.aar, input.bhg, ignore_none = False)
            def map():
                return draw_map()