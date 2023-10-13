import networkx as nx

class HCAstarMover:
    """
        Class responsible for handling the movement validation and execution of agents
    """
    def __init__(self, mapCanvas, mapGraph, sharedInfoManager):
        self.mapCanvas = mapCanvas
        self.mapGraph = mapGraph
        self.sharedInfoManager = sharedInfoManager

    def validateAgentMove(self, agent, targetNode, collisionBehavior):
        # This is handled via the reservation table

        # To handle unexpected crashes (not sure how this happens, but it probably does)
        # Ensure that the node exists in the graph
        # Ensure that the node has an edge to the target node or that target node is the current node (wait)
        # Rework reservation to store agent IDs instead of True/False
        # - Probably requires reworking of internal agent IDs to not use 0, which evaluates to false
        # - - Actually isinstance(0, int) and isinstance(0, bool) return different, so maybe its fine
        # - And then compare the reserver to the current agent, if identical it can move through the reservation
        return True