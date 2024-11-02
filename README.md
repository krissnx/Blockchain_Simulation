#### FRANÇAIS ####

**Simulation de Blockchain**

Ce projet propose une simulation simplifiée du fonctionnement d'une blockchain Proof of Work (POW), permettant aux utilisateurs d'explorer les interactions entre les mineurs, les transactions et le processus de validation des blocks.

**Structure du projet :**

- `block.py`
- `transaction.py`
- `blockchain.py`
- `mineur.py`
- `app.py`
- `templates` :
  - `index.html`

**Exécution :**

1. Exécutez le fichier principal `app.py`.

2. Ouvrez la page web dédiée à la simulation en utilisant l'URL affichée dans le terminal.

3. Appuyez sur le bouton `Start` pour lancer la simulation.

4. Utilisez les fonctionnalités de la simulation :
   - Ajoutez des mineurs et des mineurs tricheurs en appuyant sur les boutons `Ajouter un mineur/tricheur`.
   - Suivez les instructions et les logs affichés (en haut, à gauche) pour observer la simulation en cours.
   - Appuyez sur les boutons blockchain pour sélectionner la blockchain à afficher (apparaît dès la création d'une deuxième blockchain).
   - Survolez les blocks pour afficher leurs caractéristiques.
   - Les mineurs malveillants disposent d’un fond rouge lors du survol.

5. Appuyez sur le bouton `Stop` pour arrêter la simulation. Stoppez l’exécution de `app.py` pour interrompre le thread.

---

#### ENGLISH #### 

**Blockchain Simulation**

This project provides a simplified simulation of a Proof of Work (POW) blockchain, allowing users to explore the interactions between miners, transactions, and the block validation process.

**Project Structure:**

- `block.py`
- `transaction.py`
- `blockchain.py`
- `mineur.py`
- `app.py`
- `templates`:
  - `index.html`

**Execution:**

1. Run the main file `app.py`.

2. Open the web page for the simulation using the URL displayed in the terminal.

3. Press the `Start` button to launch the simulation.

4. Use the simulation features:
   - Add miners and cheating miners by clicking on the `Add Miner/Cheater` buttons.
   - Follow the instructions and logs displayed (top left) to observe the ongoing simulation.
   - Press the blockchain buttons to select the blockchain to display (appears once a second blockchain is created).
   - Hover over blocks to display their characteristics.
   - Malicious miners have a red background when hovered.

5. Press the `Stop` button to end the simulation. Stop `app.py` to terminate the thread.
