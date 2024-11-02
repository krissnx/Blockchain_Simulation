import random
import string
from block import Block
from blockchain import BlockChain
from transaction import Transaction

class Mineur:
    def __init__(self, id=None, blockchain=None, listeTransactions=None, couleur=None, solde=0, blockchainId=None, corruption = False):
        self.id = id
        self.solde = 0
        self.couleur = couleur
        self.blockchain = blockchain if blockchain else BlockChain(id=blockchainId)
        self.listeTransactions = listeTransactions if listeTransactions else []
        self.puissanceCalcul = random.randint(2, 5)
        self.corruption = corruption

    def ajouterBlock(self, block, trouve=False):
        if trouve:
            # Réception de la récompense par le mineur
            self.solde += block.recompense
        self.blockchain.listeBlocks.append(block)

    def recevoirBlock(self, block, infos=None):
        # Vérifier le bloc reçu
        if (self.blockchain.recupererDernierBlock() is None or block.hashBlockPrecedent == self.blockchain.recupererDernierBlock().calculerHash()) and (block.calculerHash())[:3] == "000":

            # Gestion des transactions récupérées dans le block
            for transaction in block.listeTransactions:
                self.solde += transaction.frais

            # print(f'Mineur {self.id} (solde = {self.strSolde()}) accepte le bloc et l\'ajoute à sa blockchain')
            if infos is not None :
                infos.append({'message': f'Mineur {self.id} accepte le bloc et l\'ajoute à sa blockchain', 'class': 'accepted'})
            self.ajouterBlock(block)
        else:
            # print(f'Mineur {self.id} refuse le bloc')
            if infos is not None :
                infos.append({'message': f'Mineur {self.id} refuse le bloc', 'class': 'refused'})

    def recevoirTransaction(self, transaction):
        self.listeTransactions.append(transaction)

    def diffuserTransaction(self, transaction, listeMineurs):
        for mineur in listeMineurs:
            mineur.recevoirTransaction(transaction)

    def connecterBlockchain(self, listeMineurs):
        # Récupération de la blockchain la plus longue parmi les mineurs
        blockchainLaPlusLongue = max(listeMineurs, key=lambda mineur: len(mineur.blockchain)).blockchain

        # Copie de la blockchain
        self.blockchain = BlockChain(id=blockchainLaPlusLongue.id)
        self.blockchain.listeBlocks = blockchainLaPlusLongue.listeBlocks.copy()

    def __str__(self):
        return f'Mineur {self.id}'

    def strSolde(self):
        return "%.7f" % self.solde

