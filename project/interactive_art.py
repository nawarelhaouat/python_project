import pygame
import random
import os
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
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_path)
    print("Son chargé avec succès !")
except pygame.error:
    print("Erreur : Fichier 'click.wav' introuvable ! Vérifie son emplacement.")
    sound = None

# Charger la police artistique
font_path = os.path.join(os.path.dirname(__file__), "fonts", "artistic.ttf")
if os.path.exists(font_path):
    font = pygame.font.Font(font_path, 30)  # Police stylisée avec taille 50
else:
    print("⚠️ Police 'artistic.ttf' introuvable ! Utilisation de la police par défaut.")
    font = pygame.font.Font(None, 50)  # Si la police n'est pas trouvée, on utilise celle par défaut

# Classe pour les papillons animés
class Papillon:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(20, 40)
        self.color = (random.randint(200, 255), random.randint(100, 200), random.randint(100, 200))
        self.speed_x = random.choice([-2, -1, 1, 2])
        self.speed_y = random.choice([-2, -1, 1, 2])
        self.angle = 0

    def dessiner(self):
        # Dessiner les ailes du papillon
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.size, self.size // 2))
        pygame.draw.ellipse(screen, self.color, (self.x + self.size // 2, self.y, self.size, self.size // 2))
        # Dessiner le corps
        pygame.draw.line(screen, (0, 0, 0), (self.x + self.size // 2, self.y + self.size // 4),
                         (self.x + self.size // 2, self.y + self.size // 2), 2)

    def bouger(self):
        self.x += self.speed_x
        self.y += self.speed_y
        # Rebondir sur les bords de l'écran
        if self.x <= 0 or self.x >= WIDTH:
            self.speed_x *= -1
        if self.y <= 0 or self.y >= HEIGHT:
            self.speed_y *= -1

# Fonction pour afficher l'écran d'explication avec animation et style artistique
def afficher_explication():
    screen.fill((0, 0, 0))  # Fond noir

    explications = [
        "WELCOME TO THE GAME!",
        "Left Click : Pick or drop a shape",
        "Press C : New color",
        "Press S : Remove",
        "Press A : Bigger",
        "Press P : Smaller",
        "Press F : New shape",
        "ENTER"
    ]

    y_offset = HEIGHT // 6
    alpha = 0  # Opacité du texte (animation)

    # Créer des papillons
    papillons = [Papillon() for _ in range(10)]

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((0, 0, 0))  # Arrière-plan noir

        # Dessiner les papillons
        for papillon in papillons:
            papillon.dessiner()
            papillon.bouger()

        # Dessiner le texte avec animation
        text_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, ligne in enumerate(explications):
            texte = font.render(ligne, True, (255, 255, 255, alpha))
            text_rect = texte.get_rect(center=(WIDTH // 2, y_offset + i * 60))  # Espacement ajusté
            text_surface.blit(texte, text_rect)

        screen.blit(text_surface, (0, 0))
        pygame.display.flip()

        if alpha < 255:
            alpha += 5  # Animation de fondu
        else:
            alpha = 255

        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False

# Attendre que l'utilisateur appuie sur "Entrée" pour démarrer
afficher_explication()

# Définition des couleurs et des formes
colors = ["cyan", "magenta", "lime", "orange", "gold", "violet", "deepskyblue", "springgreen", "hotpink", "coral"]
selected_forme = None

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

# Fonction pour jouer un son
def jouer_son():
    if sound:
        sound.play()

# Fonction pour détecter les clics sur les formes
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

# Fonction pour désélectionner toutes les formes
def deselectionner_formes():
    global selected_forme
    for forme in formes:
        forme.selected = False
    selected_forme = None

def changer_forme():
    global selected_forme
    if selected_forme:
        formes.remove(selected_forme)
        nouvelle_forme = random.choice([Carre, Cercle, Triangle, Pentagone])()
        nouvelle_forme.position = selected_forme.position
        nouvelle_forme.couleur = selected_forme.couleur
        if isinstance(selected_forme, (Carre, Triangle, Pentagone)):
            nouvelle_forme.size = selected_forme.size
        elif isinstance(selected_forme, Cercle):
            nouvelle_forme.rayon = selected_forme.rayon
        formes.append(nouvelle_forme)
        selected_forme = nouvelle_forme

# Boucle principale
running = True
while running:
    screen.fill((0, 0, 0))  # Fond noir

    for forme in formes:
        forme.dessiner()

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
                    selected_forme.size *= 1.2
                elif event.key == pygame.K_p:
                    selected_forme.size *= 0.8
                elif event.key == pygame.K_f:
                    changer_forme()
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            if selected_forme:
                selected_forme.position = list(event.pos)

    pygame.display.flip()

pygame.quit()