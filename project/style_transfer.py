import torch
torch.multiprocessing.set_start_method('spawn', force=True)
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image

# Charger et prétraiter une image
def load_image(image_path, max_size=256):
    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((max_size, max_size)),  # Taille réduite pour accélérer
        transforms.ToTensor()
    ])
    image = transform(image).unsqueeze(0)  # Ajouter une dimension batch
    return image

# Extraire les caractéristiques avec VGG19
def get_features(image, model, layers):
    features = {}
    x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[layers[name]] = x
    return features

# Calculer la matrice de Gram (mesure le style)
def gram_matrix(tensor):
    _, c, h, w = tensor.size()
    tensor = tensor.view(c, h * w)
    gram = torch.mm(tensor, tensor.t())
    return gram / (c * h * w)

# Appliquer le transfert de style optimisé
def apply_style_transfer(content_path, style_path, output_path, num_steps=100, style_weight=1e6, content_weight=1):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Charger les images
    content = load_image(content_path).to(device)
    style = load_image(style_path).to(device)

    # Charger le modèle VGG19 pré-entraîné
    vgg = models.vgg19(pretrained=True).features.to(device).eval()

    # Sélectionner les couches pour le style et le contenu
    layers = {
        '0': 'conv1_1',
        '5': 'conv2_1',
        '10': 'conv3_1',
        '19': 'conv4_1',
        '21': 'conv4_2',  # Contenu
        '28': 'conv5_1'
    }

    # Extraire les caractéristiques
    content_features = get_features(content, vgg, layers)
    style_features = get_features(style, vgg, layers)

    # Calculer les matrices de Gram pour le style
    style_grams = {layer: gram_matrix(style_features[layer]) for layer in style_features}

    # Image cible (on commence avec l’image de contenu)
    target = content.clone().requires_grad_(True).to(device)

    # Optimisation avec Adam
    optimizer = optim.Adam([target], lr=0.03)

    for step in range(num_steps):
        optimizer.zero_grad()  # ✅ Réinitialiser les gradients avant chaque itération

        target_features = get_features(target, vgg, layers)

        # ✅ Correction pour éviter l'erreur retain_graph
        content_loss = torch.mean((target_features['conv4_2'] - content_features['conv4_2'].detach()) ** 2)

        # ✅ Correction dans la perte de style
        style_loss = 0
        for layer in style_features:
            target_gram = gram_matrix(target_features[layer])
            style_gram = style_grams[layer].detach()  # ✅ Ajout de .detach() ici
            layer_loss = torch.mean((target_gram - style_gram) ** 2)
            style_loss += layer_loss

        style_loss *= style_weight
        content_loss *= content_weight

        # Perte totale
        total_loss = content_loss + style_loss

        # ✅ Réinitialiser les gradients AVANT d'appeler backward()
        total_loss.backward()
        optimizer.step()

        if step % 20 == 0:
            print(f"Étape {step}/{num_steps} - Perte totale : {total_loss.item():.2f}")

    # Sauvegarder l’image stylisée
    save_image(target, output_path)
    print(f"Image stylisée enregistrée sous {output_path}")

# Fonction pour sauvegarder l’image finale
def save_image(tensor, path):
    image = tensor.clone().detach().cpu().squeeze(0)
    image = transforms.ToPILImage()(image)
    image.save(path)
