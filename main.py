import queue
from mineur import Mineur
from block import Block
from transaction import Transaction
import random
import hashlib
import time
import matplotlib.pyplot as plt
import random

# Initialisation des données partagées
shared_queue = queue.Queue()
blockData = {}

def ajouterMineur(listeMineurs):
    nouveauMineur = Mineur(len(listeMineurs))
    nouveauMineur.connecterBlockchain(listeMineurs)
    listeMineurs.append(nouveauMineur)
    print("Nouveau mineur connecté\n\n")
    time.sleep(5)

def main():

    # Création des mineurs
    listeMineurs = []
    for i in range(5) :
        listeMineurs.append(Mineur(i))

    # Initialisation du nonce
    nonce = 0

    # Initialisation des caractéristiques des blocks
    dernierHash = None
    compteurBlocks = 0
    recompense = 6.25

    # Début de la simulation
    while 1:

        # Recherche d'un block
        nonce += 1
        hashBlock = hashlib.sha256((str(nonce)).encode()).hexdigest()
        if hashBlock[:3] == "000":

            # Choix aléatoire d'un mineur
            choix = random.randint(0, len(listeMineurs) - 1)

            # Proposition d'un block par le mineur choisi
            block = Block(dernierHash, str(nonce), recompense=recompense)
            dernierHash = hashBlock  # on garde le dernier hash en mémoire
            compteurBlocks += 1

            # Gestion des transactions
            while random.randint(0, 10) < 3:
                frais = random.random() * 0.00000030 + 0.00000010  # 10 satoshi minimum
                transaction = Transaction(listeMineurs[choix], frais)
                block.ajouterTransaction(transaction)

            listeMineurs[choix].ajouterBlock(block, True)
            message = f'Mineur {choix} (solde = {listeMineurs[choix].strSolde()}) trouve le block {compteurBlocks} et l\'ajoute à sa Blockchain'
            if len(block.listeTransactions) > 0:
                if len(block.listeTransactions) == 1:
                    message += f' (1 transaction)'
                else:
                    message += f' ({len(block.listeTransactions)} transactions)'
            print(message)
            time.sleep(random.random() * 0.5)


            # Reception du block par les autres mineurs
            for i in range(len(listeMineurs)) :
                if i != choix :
                    time.sleep(random.random() * 0.8)
                    print(f'Mineur {i} reçoit le block {compteurBlocks}')
                    listeMineurs[i].recevoirBlock(block)



            # print('\n\n')
            time.sleep(random.randint(6, 12))

            # Gestion des nouveaux mineurs
            if random.randint(1, 10) >= 9:
                ajouterMineur(listeMineurs)
                print(len(listeMineurs))

if __name__ == '__main__':
    main()
