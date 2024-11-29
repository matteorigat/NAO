import matplotlib.pyplot as plt

# Dati per emozioni (vct, rspd)
emozioni = [
    (105, 110, 'joy'),
    (105, 105, 'happy'),
    (97, 90, 'sad'),
    (90, 120, 'angry'),
    (110, 120, 'surprised'),
    (95, 115, 'fear'),
    (102, 95, 'calm')
]

# Estrai le coordinate x (vct), y (rspd) e i nomi delle emozioni
x_values = [punto[0] for punto in emozioni]
y_values = [punto[1] for punto in emozioni]
nomi = [punto[2] for punto in emozioni]

# Crea il grafico
plt.scatter(x_values, y_values, color='red', s=20)  # Aggiungi i punti come cerchi rossi

# Aggiungi etichette dei punti
for i in range(len(emozioni)):
    plt.text(x_values[i] + 1, y_values[i] + 1, nomi[i], fontsize=10, color='blue')  # Aggiungi il nome accanto al punto

plt.scatter(100, 100, color='green', s=20, label='rst')  # Punto verde al centro
plt.text(100 + 1, 100 + 1, 'rst', fontsize=10, color='green')

# Imposta i limiti degli assi
plt.xlim(70, 130)  # Limiti per l'asse x (vct)
plt.ylim(70, 130)  # Limiti per l'asse y (rspd)

# Aggiungi le linee degli assi
plt.axhline(102, color='black',linewidth=1)  # Asse orizzontale (y=0)
plt.axvline(99, color='black',linewidth=1)  # Asse verticale (x=0)

# Aggiungi etichette degli assi
plt.xlabel('VCT (Pitch)')
plt.ylabel('RSPD (Speed)')

# Mostra il grafico
plt.title('Visualizzazione delle Emozioni con VCT e RSPD')
plt.grid(True)  # Mostra la griglia
plt.show()