import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# Charger les données
file_path = "Rougeole_au_Maroc_-_100_derniers_jours.csv"
df = pd.read_csv(file_path)

# Nettoyage des données
df = df.dropna().drop_duplicates()
df["Region_Index"] = df["Region"].astype("category").cat.codes
df["Date_Index"] = df["Date"].astype("category").cat.codes

# Liste des noms des régions
region_labels = df["Region"].astype("category").cat.categories

# Création de la figure et des axes
fig = plt.figure(figsize=(16, 8))  # 🔹 Augmenter la taille globale

# Axe principal 3D
ax = fig.add_subplot(111, projection='3d')

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

# Ajouter la barre des couleurs à droite (Nombre de Cas)
cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
cbar.set_label("Nombre de Cas", color='black')
cbar.ax.yaxis.label.set_color('black')
cbar.ax.tick_params(colors='black')

# 🔹 AJOUTER UN TABLEAU D’INDEX DES RÉGIONS À GAUCHE (AGRANDI) 🔹
table_data = [[idx, region] for idx, region in enumerate(region_labels)]
table_ax = fig.add_axes([0.02, 0.2, 0.15, 0.6])  # 🔹 Élargir la table ([x, y, largeur, hauteur])
table_ax.axis("off")  # Cacher l'axe

# Affichage du tableau plus grand et plus lisible
table = table_ax.table(cellText=table_data, colLabels=["Index", "Région"], 
                       cellLoc="center", loc="center")

table.auto_set_font_size(False)
table.set_fontsize(9)  # 🔹 Augmenter la taille du texte
table.scale(1.5, 1.5)  # 🔹 Agrandir la table en largeur et hauteur

# Fonction d'animation pour la rotation
def update(frame):
    ax.view_init(elev=20, azim=frame)

# Création de l'animation
ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 360, 2), interval=50)

# Afficher le graphique animé
plt.show()
