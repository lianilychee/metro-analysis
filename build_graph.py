## Scrape info from GTFS data to build a graph of a city's transit system. ##

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

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
        self.route_ids = []
        self.trip_ids = defaultdict(lambda:[])

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
        self.extract_route_id()
        self.extract_trip_id()
        self.extract_stop_times()


    def extract_route_id(self):
        """
        From routes.txt, extract the unique route_id's based on route_type.
        """
        print 'start extract_route_id()'

        with open(self.path+"/routes.txt") as f:
            for line in f:
                if ",0," in line or ",1," in line:
                    route_id_temp = line.split(",")[0][1:-1]
                    # route_type_temp = line.split(",")[5]      TODO: reconsider if we need the route type at all
                    self.route_ids.append(route_id_temp)

        print 'end extract_route_id()\n'


    def extract_trip_id(self):
        """
        From trips.txt, extract the unique trip_ids based on route_ids.
        """
        print 'start extract_trip_id()'
        
        with open(self.path+"/trips.txt") as f:
            for line in f:
                route_id_temp = line.split(",")[0][1:-1]
                if route_id_temp in self.route_ids:
                    trip_id_temp = line.split(",")[2][1:-1]
                    if self.trip_ids[route_id_temp] == []:      # TODO - remove conditional after we finish writing extract_stop_times()
                        self.trip_ids[route_id_temp].append(trip_id_temp)

        print 'end extract_trip_id()\n'


    def extract_stop_times(self):
        """
        From stop_times.txt, extract all the stop_times based on trip_ids.
        """
        print 'start extract_stop_time()'

        # extract number of stops for any given trip_id
        with open(self.path+"/stop_times.txt") as f:

            for line in f:
                temp_list = []
                trip_id_temp = line.split(",")[0][1:-1]
                temp_list.append(trip_id_temp)

                if temp_list in self.trip_ids.values():
                    
                    print temp_list
                    print self.trip_ids.keys()



        print 'end extract_stop_time()'


    def extract_stop(self):
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
    G = Graph('boston')
    G.extract_data()