from block import Block
from datetime import datetime

class BlockChain:

    def __init__(self, id=None):
        self.id = id
        self.listeBlocks = []

    def __len__(self):
        return len(self.listeBlocks)

    def __str__(self):
        if not self.listeBlocks:
            return "Blockchain is empty."

        resultat = ""
        for i, block in enumerate(self.listeBlocks):
            resultat += f"Block {i}:\n{block}\n\n"

        return resultat

    def recupererDernierBlock(self):
        if self.listeBlocks:
            return self.listeBlocks[-1]
        else:
            return None
