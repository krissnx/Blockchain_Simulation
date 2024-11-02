from datetime import datetime
import hashlib

class Transaction:

    def __init__(self, expediteur, frais):
        self.expediteur = expediteur
        self.frais = frais
        self.date = datetime.now()


    def __str__(self):
        return f'Expediteur : {self.expediteur}\nFrais : {self.frais}'

    def verifierTransaction(self):
        min_frais = 0.00000010  # 10 satoshi minimum
        max_frais = 0.00000030  # 30 satoshi maximum

        if min_frais <= self.frais <= max_frais and self.expediteur.solde >= self.frais:
            self.expediteur -= self.frais
            return True
        else:
            print(f"Echec de la vérification de la transaction")
            return False

