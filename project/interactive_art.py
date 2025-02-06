import pygame
import random
import os
from datetime import datetime
import math

# Initialisation de pygame
pygame.init()

# Configuration de l'écran
WIDTH, HEIGHT = 1400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Generative Art avec Pygame")

# Charger le son depuis le dossier sounds/
sound_path = os.path.join(os.path.dirname(__file__), "sounds", "click.wav")
try:
    sound = pygame.mixer.Sound(sound_path)
    print("✅ Son chargé avec succès !")
except pygame.error:
    print("❌ Erreur : Fichier 'click.wav' introuvable ! Vérifie son emplacement.")
    sound = None

# Définition des couleurs et des formes
colors = ["cyan", "magenta", "lime", "orange", "gold", "violet", "deepskyblue", "springgreen", "hotpink", "coral"]
selected_forme = None

# Dossier de sauvegarde des images
image_folder = "static/"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

class Forme:
    def __init__(self):
        self.couleur = random.choice(colors)
        self.position = [random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)]
        self.selected = False

    def dessiner(self):
        pass

class Carre(Forme):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 100)

    def dessiner(self):
        pygame.draw.rect(screen, pygame.Color(self.couleur), (*self.position, self.size, self.size))

class Cercle(Forme):
    def __init__(self):
        super().__init__()
        self.rayon = random.randint(20, 50)

    def dessiner(self):
        pygame.draw.circle(screen, pygame.Color(self.couleur), self.position, self.rayon)

class Triangle(Forme):
    def __init__(self):
        super().__init__()
        self.size = random.randint(30, 80)

    def dessiner(self):
        x, y = self.position
        points = [(x, y - self.size), (x - self.size, y + self.size), (x + self.size, y + self.size)]
        pygame.draw.polygon(screen, pygame.Color(self.couleur), points)

class Pentagone(Forme):
    def __init__(self):
        super().__init__()
        self.size = random.randint(30, 70)

    def dessiner(self):
        x, y = self.position
        points = [
            (x + self.size * math.cos(math.radians(i * 72)), y + self.size * math.sin(math.radians(i * 72)))
            for i in range(5)
        ]
        pygame.draw.polygon(screen, pygame.Color(self.couleur), points)

# Génération des formes
formes = [random.choice([Carre, Cercle, Triangle, Pentagone])() for _ in range(20)]

def jouer_son():
    if sound:
        sound.play()

def detection(x, y):
    global selected_forme
    for objet in formes:
        obj_x, obj_y = objet.position
        if obj_x - 50 <= x <= obj_x + 50 and obj_y - 50 <= y <= obj_y + 50:
            selected_forme = objet
            selected_forme.selected = True
            return
    nouvel_objet = random.choice([Carre, Cercle, Triangle, Pentagone])()
    nouvel_objet.position = [x, y]
    formes.append(nouvel_objet)
    jouer_son()

def deselectionner_formes():
    global selected_forme
    for forme in formes:
        forme.selected = False
    selected_forme = None

running = True
while running:
    screen.fill((0, 0, 0))  # Remplir l'écran avant de dessiner les formes
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            detection(x, y)
        elif event.type == pygame.KEYDOWN:
            if selected_forme:
                if event.key == pygame.K_c:
                    selected_forme.couleur = random.choice(colors)
                elif event.key == pygame.K_s:
                    formes.remove(selected_forme)
                    deselectionner_formes()
                elif event.key == pygame.K_a:
                    if isinstance(selected_forme, (Carre, Triangle, Pentagone)):
                        selected_forme.size *= 1.2
                    elif isinstance(selected_forme, Cercle):
                        selected_forme.rayon *= 1.2
                elif event.key == pygame.K_p:
                    if isinstance(selected_forme, (Carre, Triangle, Pentagone)):
                        selected_forme.size *= 0.8
                    elif isinstance(selected_forme, Cercle):
                        selected_forme.rayon *= 0.8
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            if selected_forme:
                selected_forme.position = list(event.pos)

    for forme in formes:
        forme.dessiner()
    
    pygame.display.flip()

pygame.quit()