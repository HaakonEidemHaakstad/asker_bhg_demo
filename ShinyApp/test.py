import pandas as pd
import numpy as np
import seaborn as sns

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
#print(df_copy)
#justeringshistorikk = pd.DataFrame(columns = ["År", "Område", "Justering", "Ny kapasitet", "Kommentar"])
#for i in range(len(justeringshistorikk.columns[:])):
#      justeringshistorikk.iloc[:, i] = [j for j in range(10)]

#justeringslog = []
#for i in range(justeringshistorikk.shape[0]):
#      justeringslog.append(justeringshistorikk.iloc[i, :].tolist())

justeringshistorikk = pd.read_csv("/home/haakon/Downloads/justeringslogg 2024-10-09 13_32_02.csv")
#print(justeringshistorikk.values)
justeringslog = []
def opplastet_log():
      global justeringslog
      global df_copy
      global justeringshistorikk
      df_copy.iloc[:, :] = df.iloc[:, :].copy()
      justeringslog = [i for i in justeringshistorikk.values.tolist()]
      for i in justeringshistorikk.values:
            rowindex = df_copy.iloc[:, 0].tolist().index(i[0])
            colindex = df_copy.columns.tolist().index(i[1])
            df_copy.iloc[rowindex:, colindex] = [j + i[2] for j in df_copy.iloc[rowindex:, colindex]]

#print(pd.DataFrame({"Test1": [], "Test2": [], "Test3": []}))
import matplotlib.pyplot as plt
import numpy as np

# Create some data
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

# Create plot
fig, ax = plt.subplots()
line, = ax.plot(x, y)
plt.show()

# Update the data
#y_new = np.cos(x)  # Update y values
#line.set_ydata(y_new)

# Redraw the plot
#plt.draw()