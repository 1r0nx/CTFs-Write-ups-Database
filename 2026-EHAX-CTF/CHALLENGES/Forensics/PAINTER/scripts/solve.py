import matplotlib.pyplot as plt
import struct

x, y = 0, 0
segments = []
current_segment = []

# Paramètres d'ajustement
stretch_factor = 1.5  # Augmente l'espace horizontal global
spacing_between_strokes = 150 # Espace ajouté à chaque fois que le stylo se lève

with open("data.txt", "r") as f:
    for line in f:
        line = line.strip()
        if len(line) < 14: continue
        
        data = bytes.fromhex(line)
        dx = struct.unpack('<h', data[2:4])[0]
        dy = struct.unpack('<h', data[4:6])[0]
        
        new_x = x + dx
        new_y = y + dy
        
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 50:
            current_segment.append((new_x * stretch_factor, -new_y))
        else:
            if current_segment:
                segments.append(current_segment)
                # On simule un petit pas vers la droite pour ne pas superposer
                x += spacing_between_strokes 
            current_segment = [(new_x * stretch_factor, -new_y)]
            
        x, y = new_x, new_y

if current_segment:
    segments.append(current_segment)

# Affichage en grand format
plt.figure(figsize=(20, 10)) # Fenêtre très large
for seg in segments:
    if len(seg) > 2:
        sx, sy = zip(*seg)
        plt.plot(sx, sy, linewidth=2)

plt.axis('equal')
plt.grid(True, linestyle='--', alpha=0.5) # Grille pour aider l'œil
plt.title("Flag Reconstruction - Expanded View")
plt.show()