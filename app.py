import copy
import string
from flask import Flask, render_template, request
from flask import jsonify
from block import Block
from mineur import Mineur
from transaction import Transaction
import threading
import time
import queue
import hashlib
import random

app = Flask(__name__)

# Initialisation des données partagées
shared_queue = queue.Queue()
lock = threading.Lock()
listeMineurs = []
finSimulation = False

# Initialisation des couleurs
couleurs = ['#E84B4B', '#E8784B', '#E8B14B', '#E8E34B', '#A3E84B', '#59E84B', '#4BE89C', '#4BE8E1', '#4B97E8', '#4B4DE8', '#954BE8', '#DE4BE8', '#E84BAF', '#E84B7D', '#461D81']
random.shuffle(couleurs)

@app.route('/run_simulation', methods=['GET'])
def run_simulation():
    threading.Thread(target=simulationBlockchain).start()
    return {'status': 'ok'}

@app.route('/get_block_data', methods=['GET'])
def get_block_data():
    try:
        if request.args.get('action') == '1':
            ajouterMineur(listeMineurs)

        if request.args.get('action') == '2':
            supprimerMineur(listeMineurs, request.args.get('selectedMiner'))

        if request.args.get('action') == '3':
            ajouterMineur(listeMineurs, True)

        simulation_data = shared_queue.get_nowait()

    except queue.Empty:
        simulation_data = {'status': 'ko'}

    return jsonify(simulation_data)

@app.route('/stop_simulation', methods=['GET'])
def stop_simulation():
    global finSimulation
    finSimulation = True
    return {'status': 'ok'}


@app.route('/')
def index():
    return render_template('index.html')


def ajouterMineur(listeMineurs, corruption=False):
    lock.acquire()
    id = listeMineurs[-1].id + 1
    couleur = couleurs[(id + 1) % len(couleurs)]
    nouveauMineur = Mineur(id, couleur=couleur, corruption=corruption)
    nouveauMineur.connecterBlockchain(listeMineurs)
    listeMineurs.append(nouveauMineur)
    nombreMineurs = len(listeMineurs)
    shared_queue.put({'nb_miners': nombreMineurs, 'infos': [{'message': f"Nouveau mineur connecté (Mineur {id})", 'class': 'info'}], 'miners_data': [{'id': id, 'balance': listeMineurs[-1].strSolde(), 'color': listeMineurs[-1].couleur, 'blockchain': listeMineurs[-1].blockchain.id, 'corruption': listeMineurs[-1].corruption, 'puissance': listeMineurs[-1].puissanceCalcul}], 'action': 'add'})
    lock.release()


def supprimerMineur(listeMineurs, id):
    lock.acquire()
    for mineur in listeMineurs:
        if id == str(mineur.id):
            listeMineurs.remove(mineur)
            nombreMineurs = len(listeMineurs)
            shared_queue.put({'nb_miners': nombreMineurs, 'infos': [{'message': f"Mineur {id} déconnecté", 'class': 'info'}], 'action': 'delete'})
            break
    lock.release()


def broadcasting(choix, infos, block):
    for i in range(len(listeMineurs)):
        if i != choix and listeMineurs[i].blockchain.id == listeMineurs[choix].blockchain.id:
            time.sleep(random.random() * 0.8)
            infos.append({'message': f'Mineur {listeMineurs[i].id} reçoit le block {block.id}', 'class': 'default'})
            listeMineurs[i].recevoirBlock(block, infos)


def envoiDonnees(mineursData, block, choix, infos, forkBlock=None, forkChoix=None):
    for mineur in listeMineurs:
        mineursData.append({'id': mineur.id, 'balance': mineur.strSolde(), 'color': mineur.couleur, 'blockchain': mineur.blockchain.id, 'corruption': mineur.corruption, 'puissance': mineur.puissanceCalcul})

    blockData = {'number': block.id, 'hash': block.hashBlockPrecedent, 'nonce': block.nonce,
                 'date': block.dateCreation.strftime("%m/%d/%Y %H:%M:%S"), 'miner': listeMineurs[choix].id,
                 'color': listeMineurs[choix].couleur,
                 'blockchain': listeMineurs[choix].blockchain.id}
    donnees = {'nb_miners': len(listeMineurs), 'block_data': blockData, 'miners_data': mineursData, 'infos': infos}

    if forkBlock != None:
        forkData = {'number': forkBlock.id, 'hash': forkBlock.hashBlockPrecedent, 'nonce': forkBlock.nonce,
                     'date': forkBlock.dateCreation.strftime("%m/%d/%Y %H:%M:%S"), 'miner': listeMineurs[forkChoix].id,
                     'color': listeMineurs[forkChoix].couleur,
                     'blockchain': listeMineurs[forkChoix].blockchain.id}
        donnees['fork_data'] = forkData

    shared_queue.put(donnees)


def gestionTranscations(choix, block):
    while random.randint(0, 10) < 3:
        frais = random.random() * 0.00000030 + 0.00000010  # 10 satoshi minimum
        transaction = Transaction(listeMineurs[choix], frais)
        block.ajouterTransaction(transaction)

def choixMineurs(listeMineurs, totalBlockchains):
    if totalBlockchains < 2:
        return random.choices(range(len(listeMineurs)), weights=[mineur.puissanceCalcul for mineur in listeMineurs])[0]
    else:
        blockchains = {}
        for mineur in listeMineurs:
            if mineur.blockchain.id not in blockchains:
                blockchains[mineur.blockchain.id] = []
            blockchains[mineur.blockchain.id].append(mineur)

        blockchainsPuissanceCalcul = {}
        for blockchain, mineurs in blockchains.items():
            blockchainsPuissanceCalcul[blockchain] = sum(mineur.puissanceCalcul for mineur in mineurs)

        blockchainChoisie = random.choices(list(blockchains.keys()), weights=list(blockchainsPuissanceCalcul.values()))[0]
        choixMineur = random.choice(blockchains[blockchainChoisie])
        return listeMineurs.index(choixMineur)

def choixPuissanceCalcul(listeMineurs):
    puissanceCalculTotal = sum(mineur.puissanceCalcul for mineur in listeMineurs)
    puissanceCalculBlockchains = {}
    for mineur in listeMineurs:
        puissanceCalculBlockchains.setdefault(mineur.blockchain.id, 0)
        puissanceCalculBlockchains[mineur.blockchain.id] += mineur.puissanceCalcul
    probabilites = {blockchain: puissanceCalcul / puissanceCalculTotal for blockchain, puissanceCalcul in
                    puissanceCalculBlockchains.items()}
    valeurAleatoire = random.uniform(0, 1)
    probabilitesCumules = 0
    for blockchain, probabilite in probabilites.items():
        probabilitesCumules += probabilite
        if valeurAleatoire < probabilitesCumules:
            choixBlockchain = blockchain
            break
    return choixBlockchain


def simulationBlockchain():

    infos = []

    # Création des mineurs
    for i in range(3) : #
        couleur = couleurs[i % len(couleurs)]
        listeMineurs.append(Mineur(i, couleur=couleur, blockchainId='A'))

    # Ajout du tricheur
    listeMineurs.append(Mineur(3, couleur=couleurs[3 % len(couleurs)], blockchainId='A', corruption=True))

    # Initialisation du nonce
    nonce = 0

    # Initialisation des caractéristiques de la blockchain et des blocks
    totalBlockchains = 1
    infosBlockchains = {'A': {'compteurBlocks': 0, 'dernierHash': None}}
    recompense = 6.25
    reserveBlock = None

    # Initialisation des données des mineurs à envoyer
    mineursData = []
    for mineur in listeMineurs:
        mineursData.append({'id': mineur.id, 'balance': mineur.strSolde(), 'color': mineur.couleur, 'blockchain': mineur.blockchain.id, 'corruption': mineur.corruption, 'puissance': mineur.puissanceCalcul})
        infos.append({'message': f"Nouveau mineur connecté (Mineur {mineur.id})", 'class': 'info'})

    # Envoi des données initiales
    shared_queue.put({'nb_miners': len(listeMineurs), 'miners_data': mineursData, 'infos': infos})

    infos = []
    mineursData = []

    # Début de la simulation
    while not finSimulation:

        # Recherche d'un block
        nonce += 1
        hashBlock = hashlib.sha256((str(nonce)).encode()).hexdigest()
        if hashBlock[:3] == "000":

            lock.acquire()

            # Choix aléatoire d'un mineur
            choix = choixMineurs(listeMineurs,totalBlockchains)

            # Incrémentation du nombre de block dans la blockchain correspondante
            blockchainId = listeMineurs[choix].blockchain.id
            infosBlockchains[blockchainId]['compteurBlocks'] += 1

            # Proposition d'un block par le mineur choisi
            blockId = f'{listeMineurs[choix].blockchain.id}.{infosBlockchains[blockchainId]["compteurBlocks"]}' if totalBlockchains > 1 else infosBlockchains[blockchainId]['compteurBlocks']
            block = Block(blockId, infosBlockchains[blockchainId]['dernierHash'], str(nonce), recompense=recompense)
            infosBlockchains[blockchainId]['dernierHash'] = hashBlock  # on garde le dernier hash en mémoire

            # Pour une meilleure simulation, pas de triche avant le 2eme block
            if listeMineurs[choix].corruption and infosBlockchains['A']['compteurBlocks'] > 2:
                if reserveBlock is None:
                    reserveBlock = {'mineur': listeMineurs[choix], 'block': copy.deepcopy(block), 'choix': choix}
                    shared_queue.put({'infos': [{'message': f'Mineur {listeMineurs[choix].id} trouve le block {block.id} mais ne le broadcast pas', 'class': 'refused'}]})
                    infosBlockchains[blockchainId]['compteurBlocks'] -= 1
                else:
                    infosBlockchains[blockchainId]['compteurBlocks'] += 1
                    block.id = f'{listeMineurs[choix].blockchain.id}.{infosBlockchains[blockchainId]["compteurBlocks"]}' if totalBlockchains > 1 else infosBlockchains[blockchainId]["compteurBlocks"]
                    blockData = {'number': reserveBlock['block'].id, 'hash': reserveBlock['block'].hashBlockPrecedent, 'nonce': reserveBlock['block'].nonce, 'date': reserveBlock['block'].dateCreation.strftime("%m/%d/%Y %H:%M:%S"),  'miner': listeMineurs[choix].id, 'color': listeMineurs[choix].couleur, 'blockchain': listeMineurs[choix].blockchain.id}
                    shared_queue.put({'block_data': blockData})
                    blockData = {'number': block.id, 'hash': block.hashBlockPrecedent, 'nonce': block.nonce, 'date': block.dateCreation.strftime("%m/%d/%Y %H:%M:%S"), 'miner': listeMineurs[choix].id, 'color': listeMineurs[choix].couleur, 'blockchain': listeMineurs[choix].blockchain.id}
                    shared_queue.put({'nb_miners': len(listeMineurs), 'block_data': blockData, 'miners_data': mineursData, 'infos': [{'message': f'Mineur {listeMineurs[choix].id} trouve le block {block.id} et broadcast les 2 blocks à la suite (triche réussie)', 'class': 'refused'}]})
                    listeMineurs[choix].ajouterBlock(reserveBlock['block'], True)
                    broadcasting(choix, infos, reserveBlock['block'])
                    listeMineurs[choix].ajouterBlock(block, True)
                    broadcasting(choix, infos, block)
                    reserveBlock = None
            else:
                if reserveBlock is None or listeMineurs[reserveBlock['choix']].blockchain.id != listeMineurs[choix].blockchain.id:

                    # Gestion des transactions
                    gestionTranscations(choix, block)

                    listeMineurs[choix].ajouterBlock(block, True)
                    message = f'Mineur {listeMineurs[choix].id} trouve le block {block.id} et l\'ajoute à sa Blockchain'
                    if len(block.listeTransactions) > 0:
                        if len(block.listeTransactions) == 1:
                            message += f' (1 transaction)'
                        else:
                            message += f' ({len(block.listeTransactions)} transactions)'

                    infos.append({'message': message, 'class': 'info'})
                    time.sleep(random.random() * 0.5)

                    # Reception du block par les autres mineurs
                    broadcasting(choix, infos, block)

                    # Envoi des données
                    mineursData = []
                    envoiDonnees(mineursData, block, choix, infos)

                else:
                    valeurAleatoire = random.uniform(0, 1)
                    nouvelleBlockchainId = list(string.ascii_uppercase)[totalBlockchains]
                    totalBlockchains += 1
                    if valeurAleatoire < listeMineurs[choix].puissanceCalcul / (listeMineurs[choix].puissanceCalcul + reserveBlock['mineur'].puissanceCalcul):
                        infosBlockchains[nouvelleBlockchainId] = {'compteurBlocks': infosBlockchains[blockchainId]["compteurBlocks"], 'dernierHash': reserveBlock['block'].calculerHash()}
                        block.hashBlockPrecedent = reserveBlock['block'].hashBlockPrecedent

                        # Gestion des transactions
                        gestionTranscations(choix, block)

                        listeMineurs[choix].ajouterBlock(block, True)
                        listeMineurs[reserveBlock['choix']].ajouterBlock(reserveBlock["block"], True)

                        message = f'Mineur {listeMineurs[choix].id} trouve le block {block.id} et l\'ajoute à sa Blockchain'
                        if len(block.listeTransactions) > 0:
                            if len(block.listeTransactions) == 1:
                                message += f' (1 transaction)'
                            else:
                                message += f' ({len(block.listeTransactions)} transactions)'

                        infos.append({'message': message, 'class': 'info'})
                        infos.append({'message': f'Mineur {listeMineurs[reserveBlock["choix"]].id} n\'a pas réussi à tricher (fork)', 'class': 'refused'})

                        block.id = f'{listeMineurs[choix].blockchain.id}.{infosBlockchains[blockchainId]["compteurBlocks"]}'
                        reserveBlock['block'].id = f'{nouvelleBlockchainId}.{infosBlockchains[blockchainId]["compteurBlocks"]}'

                        time.sleep(random.random() * 0.5)

                        # Reception du block par les autres mineurs
                        broadcasting(choix, infos, block)
                        reserveBlock['mineur'].blockchain.id = nouvelleBlockchainId

                        # Envoi des données
                        mineursData = []
                        envoiDonnees(mineursData, block, choix, infos, reserveBlock['block'], reserveBlock['choix'])
                        listeMineurs[reserveBlock["choix"]].corruption = False
                    else:
                        print('tmp3-2')
                        infosBlockchains[nouvelleBlockchainId] = {'compteurBlocks': infosBlockchains[blockchainId]["compteurBlocks"],'dernierHash': block.calculerHash()}
                        infosBlockchains[blockchainId]['dernierHash'] = reserveBlock['block'].calculerHash()

                        listeMineurs[reserveBlock['choix']].ajouterBlock(reserveBlock["block"], True)
                        listeMineurs[choix].ajouterBlock(block, True)

                        message = f'Mineur {listeMineurs[choix].id} trouve le block {reserveBlock["block"].id} mais Mineur {listeMineurs[reserveBlock["choix"]].id} broadcast son block aussitôt (fork)'
                        infos.append({'message': message, 'class': 'refused'})

                        block.id = f'{nouvelleBlockchainId}.{infosBlockchains[blockchainId]["compteurBlocks"]}'
                        reserveBlock['block'].id = f'{listeMineurs[reserveBlock["choix"]].blockchain.id}.{infosBlockchains[blockchainId]["compteurBlocks"]}'

                        infos.append({'message': f'Le block ({block.id}) de Mineur {listeMineurs[choix].id} est refusé', 'class': 'refused'})

                        time.sleep(random.random() * 0.5)

                        # Reception du block par les autres mineurs
                        broadcasting(reserveBlock["choix"], infos, reserveBlock['block'])
                        listeMineurs[choix].blockchain.id = nouvelleBlockchainId

                        # Envoi des données
                        mineursData = []
                        envoiDonnees(mineursData, reserveBlock['block'], reserveBlock["choix"], infos, block, choix)

                    # Suppression du block réservé
                    reserveBlock = None

                    ###### Animation à faire

            lock.release()


            # Listes de données vidées
            infos = []
            mineursData = []

            time.sleep(random.randint(6, 12))




if __name__ == '__main__':
    app.run(debug=True)
