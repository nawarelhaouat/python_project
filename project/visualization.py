import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk

# Charger les données
file_path = "Rougeole_au_Maroc_-_100_derniers_jours.csv"
df = pd.read_csv(file_path)

# Nettoyage des données
df = df.dropna().drop_duplicates()
df["Region_Index"] = df["Region"].astype("category").cat.codes
df["Date_Index"] = df["Date"].astype("category").cat.codes

# Liste des noms des régions
region_labels = df["Region"].astype("category").cat.categories

# 🔹 Taille de la figure adaptée
fig = plt.figure(figsize=(15, 5))  # Ajustez la taille de la figure

# Axe principal 3D
ax = fig.add_subplot(111, projection='3d')

# 🔹 Réduire la taille du graphe et bien le centrer
ax.set_position([0.58, 0.4, 0.3, 0.3])  # Ajustement pour réduire et bien centrer
ax.set_box_aspect([0.5, 0.5, 0.5])  # Réduction équilibrée du graphe

# Variables pour le graphique
x = df["Region_Index"]
y = df["Date_Index"]
z = df["Cas_Rouge"]

# Création de la surface 3D avec une colormap "inferno"
surf = ax.plot_trisurf(x, y, z, cmap="inferno")

# Ajouter les labels des axes
ax.set_xlabel("Index Région")
ax.set_ylabel("Jour")
ax.set_zlabel("Cas de Rougeole")
ax.set_title("Les Cas de Rougeole au Maroc")

# Ajouter la barre des couleurs à droite (Nombre de Cas) et la déplacer un peu plus à droite
cbar = fig.colorbar(surf, ax=ax, shrink=0.4, aspect=8, pad=0.05)  # Ajusté avec un 'pad' plus grand

cbar.set_label("Nombre de Cas", color='white', fontweight='bold')
cbar.ax.yaxis.label.set_color('white')
cbar.ax.tick_params(colors='white')

# 🔹 AJOUTER UN TABLEAU D’INDEX DES RÉGIONS À GAUCHE 🔹
table_data = [[idx, region] for idx, region in enumerate(region_labels)]
table_ax = fig.add_axes([0.05, 0.2, 0.2, 0.6])  # Ajustez la position et la taille du tableau
table_ax.axis("off")  # Cacher l'axe

# Affichage du tableau
table = table_ax.table(cellText=table_data, colLabels=["Index", "Région"], 
                       cellLoc="center", loc="center")

table.auto_set_font_size(False)
table.set_fontsize(8)  # Ajustez la taille de la police
table.scale(1.2, 1.2)  # Ajustez l'échelle du tableau

# 🔹 Changement de l'arrière-plan en noir et texte en blanc et gras 🔹
fig.patch.set_facecolor('black')  
ax.set_facecolor('black')

# Changer les couleurs des axes et des labels
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.zaxis.label.set_color('white')
ax.title.set_color('white')

# Mettre les labels et les ticks en blanc et en gras
ax.xaxis.label.set_fontweight('bold')
ax.yaxis.label.set_fontweight('bold')
ax.zaxis.label.set_fontweight('bold')
ax.title.set_fontweight('bold')

ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.tick_params(axis='z', colors='white')

# Changer la couleur du tableau et du texte
table_ax.set_facecolor('black')
for key, cell in table._cells.items():
    cell.set_facecolor('black')  # Fond noir
    cell.set_edgecolor('white')  # Bordures blanches
    cell.set_text_props(color='white', fontweight='bold')  # Texte blanc et gras

# Fonction d'animation pour la rotation
def update(frame):
    ax.view_init(elev=20, azim=frame)

# Création de l'animation
ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 360, 2), interval=50)

# 🔹 METTRE LA FENÊTRE EN MODE FENÊTRÉ (NI MAXIMISÉ, NI PLEIN ÉCRAN) 🔹
root = tk.Tk()
root.withdraw()  # Cacher la fenêtre Tkinter
plt.get_current_fig_manager().window.resizable(False, False)  # Taille fixe


screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()


manager = plt.get_current_fig_manager()


manager.window.update_idletasks() 
window_width = manager.window.winfo_width()
window_height = manager.window.winfo_height()


window_x = 15
 
window_y = screen_height // 5  


manager.window.geometry(f"+{window_x}+{window_y}")


plt.show()