## Scrape info from GTFS data to build a graph of a city's transit system. ##

import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    """
    This class scrapes info from GTFS data to build a graph of a city's transit system.
    """

    def __init__(self, city):
        """
        Initialize class.

        Args:
            city (str): city name
        """
        self.path = 'gtfs_data/' + city     # filepath to GTFS data
        self.nodes = []
        self.edges = []         # [(node, node, weight), (node, node, weight)]

    def extract_data(self):
        """
        Open relevant GTFS file, scrape data.
        Return list of nodes, list of edges, pertinent attrs.
        """
        # err, basically a ton of work here.  There may be more sub-methods; depends how I want to architect (or, how many times I have to open/close a text file)

        # from trips.txt, determine which "trip_id" we should be looking for
        # with that trip_id, we want to open stop_times.txt, making another file that only contains the lines with said trip_id's

        # with this new text file, we should be able to calculate the average time between each stop
        # this average time betw stops will become our edges weight
        pass

    def build_graph(self):
        """
        Given the list of nodes, list of edges, and pertinent attrs, build the graph.
        Args:
            nodes (list)
        """
        G = nx.Graph()
        G.add_nodes_from()

    # def plot_graph(self):
    # I don't know what all is involved in getting the node names and edge weights to display; need to double check with Shruti


if __name__ == '__main__':
    Graph('boston')