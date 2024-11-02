from datetime import datetime
import hashlib
from transaction import Transaction


class Block:
    def __init__(self, id=None, hashBlockPrecedent=None , nonce=0 , listeTransactions = [], recompense=0):
        self.id = id
        self.dateCreation = datetime.now()
        self.hashBlockPrecedent = hashBlockPrecedent
        self.listeTransactions = listeTransactions
        self.nonce = nonce
        self.recompense = recompense


    def __str__(self):
        affichageTransactions = ""
        for i in range (0,len(self.listeTransactions)):
            affichageTransactions += f'Transaction {i} :\n' + self.listeTransactions[i].__str__() + '\n\n'
        return f'Date de création : {self.dateCreation}\nHash du block précédent : {self.hashBlockPrecedent}\nNonce : {self.nonce}\nListe des transactions :\n\n{affichageTransactions}'

    def calculerHash(self) :
        return hashlib.sha256(self.nonce.encode()).hexdigest()

    def ajouterTransaction(self, transaction):
        self.listeTransactions.append(transaction)
