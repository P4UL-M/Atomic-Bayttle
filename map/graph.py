from math import e
import random
import os

class Graphe:
    "class of the graph that will be used to created the map"
    def __init__(self, directory):
        self.directory=directory
        # key : (str) id | value : (list) linked neighboors
        self.all_graph={}
        self.name_all_graphe={}
        
        # matrix of self.height dimensions containing (str) id of nodes
        self.matrix_of_node=[]
        self.height=3
        self.width=3
        nbr_max_id=0    
        
        # filling of the self.all_width list
        for _ in range(self.height):
            self.matrix_of_node.append([])
            for _ in range(self.width):
                self.all_graph[str(nbr_max_id)]=[]
                self.name_all_graphe[str(nbr_max_id)]=None
                self.matrix_of_node[-1].append(str(nbr_max_id))
                nbr_max_id+=1
                
        self._add_all_path()    
        self._remove_random_nodes()            
        self._remove_random_path()

    def _add_all_path(self):
        """fill all path possibles from self.matrix of node, that is full at the time"""
        for id, list_of_neighboor in self.all_graph.items():
            neighboors=self.get_neighboors(id)
            for neighboor in neighboors:
                list_of_neighboor.append(neighboor)
     
    def _remove_random_nodes(self):

        # the prog try to remove half of the nodes but i'll change since if it break a path it put again the node
        for _ in range(round(self.height*self.width*0.5)):
            node_to_remove=random.choice(list(self.all_graph.keys()))
            neighboor_node_to_remove=self.get_neighboors(node_to_remove)
            del self.all_graph[node_to_remove]
            for neighboor in neighboor_node_to_remove:
                self.all_graph[neighboor].remove(node_to_remove)
            bool=True
            # if the path from all the neighboor of the node we removed doesnt exist anymore we put again the node
            for neighboor1 in neighboor_node_to_remove:
                for neighboor2 in neighboor_node_to_remove:
                    if self.get_shortest_path(neighboor1, neighboor2)==None:
                        bool=False
            if not bool:
                self.all_graph[node_to_remove]=neighboor_node_to_remove
                for neighboor in neighboor_node_to_remove:
                    self.all_graph[neighboor].append(node_to_remove)
            else:
                # from the time we only removed the node from self.all_graphe so we now need to remove it from self.matrix_of_node
                line, index=self.get_line_index_in_matrix(node_to_remove)
                self.matrix_of_node[line][index]=None
        
    def _remove_random_path(self):
        """remove 1 or 0 random path from all nodes, doest remove the path if it break the total path of the map"""
        for node in self.all_graph.keys():
            neighboor_to_remove=random.choice(self.all_graph[node])
            self.all_graph[node].remove(neighboor_to_remove)
            self.all_graph[neighboor_to_remove].remove(node)
            if self.get_shortest_path(node, neighboor_to_remove)==None:
                self.all_graph[node].append(neighboor_to_remove)
                self.all_graph[neighboor_to_remove].append(node)
    
    def seperate_by_region(self):
        """Seperate by 4 regions / biomes, each start at each corner of the map
        add 1 node to each region each iteration, the node must not be attributed to an other region"""
        NW=str(min([int(key) for key in self.all_graph.keys() if self.name_all_graphe[key]==None]))
        NE=self.get_top_right_node()
        SW=self.get_bot_left_node()
        SE=str(max([int(key) for key in self.all_graph.keys() if self.name_all_graphe[key]==None]))
        
        liste_pile=[[NW], [NE], [SW], [SE]]
        view=[NW, NE, SW, SE]
        # while all piles in liste_pile are not empty
        while len([1 for pile in liste_pile if len(pile)>0])>0:
            for i, pile in enumerate(liste_pile): 
                if len(pile)>0:
                    current_node=pile.pop(0)
                    # while the node is attributed to a region and while the pile is not empty
                    while self.name_all_graphe[current_node]!=None and len(pile)>0:
                        current_node=pile.pop(0)
                    if self.name_all_graphe[current_node]==None:    
                        self.name_all_graphe[current_node]=str(i+1)
                        for node in self.all_graph[current_node]:
                            if node not in view and self.name_all_graphe[node]==None:
                                view.append(node)
                                pile.append(node)

    def get_position_node(self, node):
        """return the position of the node in parameter from self.matrix_of_node"""
        for i, line in enumerate(self.matrix_of_node):
            for y, n in enumerate(line):
                if n == node: return (i, y)

    def get_type_node(self, node):
        """return the type of a node, the type is different in function of the openess of the map"""
        if node == None:
            return "empty", False, False
        W, E, N, S = False, False, False, False
        for neighboor in self.all_graph[node]:
            pos_node=self.get_position_node(node)
            if self.get_position_node(neighboor)[1] < pos_node[1]: W=True
            elif self.get_position_node(neighboor)[1] > pos_node[1]: E=True
            elif self.get_position_node(neighboor)[0] < pos_node[0]: N=True
            elif self.get_position_node(neighboor)[0] > pos_node[0]: S=True
        
        if W and E and N and S : return 1, E, S
        elif W and E and N : return 2, E, S
        elif W and E and S : return 3, E, S
        elif N and E and S : return 4, E, S
        elif N and W and S : return 5, E, S
        elif W and N : return 6, E, S
        elif W and E : return 7, E, S
        elif W and S : return 8, E, S
        elif N and E : return 9, E, S
        elif N and S : return 10 , E, S
        elif S and E : return 11, E, S
        elif N : return 12, E, S
        elif E : return 13, E, S
        elif S : return 14, E, S
        elif W : return 15, E, S               
    
    def get_bot_left_node(self):
        """get the node that is the most on the south west, can cause a crash if the map is tiny"""
        i=len(self.matrix_of_node)-1 ; y=0
        c_i=0;c_y=0
        while self.matrix_of_node[i][y] ==None:
            if c_i > c_y : 
                i-=1
                c_y+=1
            else: 
                y+=1
                c_i+=1
        return self.matrix_of_node[i][y]

    def get_top_right_node(self):
        """get the node that is the most on the north east, can cause a crash if the map is tiny"""
        i=0 ; y=len(self.matrix_of_node[0])-1
        c_i=0;c_y=0
        while self.matrix_of_node[i][y] ==None:
            if c_i < c_y : 
                i+=1
                c_y+=1
            else: 
                y-=1
                c_i+=1
        return self.matrix_of_node[i][y]
        
    def get_number_node(self):
        x=0
        for line in self.matrix_of_node:
            for node in line:
                if node != None: x+=1
        return x
    
    def get_shortest_path(self, start, end):
        """simple graphe shortest path function"""
        pile=[]
        vu=[start]
        pile.append([start])
        while len(pile)>0:
            current_path=pile.pop(0)
            for node in self.all_graph[current_path[-1]]:
                if node == end:
                    return current_path+[node]
                if node not in vu:
                    vu.append(node)
                    pile.append(current_path+[node])
        return None
    
    def get_line_index_in_matrix(self, id):
        line_of_id=-1 ; index_of_id=-1 ; i=0 ; y=0
        for line in self.matrix_of_node:
            for node in line:
                if node == id:
                    line_of_id=i
                    index_of_id=y
                y+=1
            i+=1
            y=0
        return line_of_id, index_of_id
        
    def get_neighboors(self, id):
        """ id : (str) the id of the node we want to compute what neighboors it has
        return a list containing the id of its neighboors"""
        
        line_of_id, index_of_id= self.get_line_index_in_matrix(id)
                
        neighboors=[]    
        
        # add all neighboors that the node have    
        if self.matrix_of_node[line_of_id][0] != id and self.matrix_of_node[line_of_id][index_of_id-1]!=None : neighboors.append(self.matrix_of_node[line_of_id][index_of_id-1])
        if self.matrix_of_node[line_of_id][-1] != id and self.matrix_of_node[line_of_id][index_of_id+1]!=None : neighboors.append(self.matrix_of_node[line_of_id][index_of_id+1])
        if line_of_id>0:
            if len(self.matrix_of_node[line_of_id-1])-1>=index_of_id and self.matrix_of_node[line_of_id-1][index_of_id]!=None: neighboors.append(self.matrix_of_node[line_of_id-1][index_of_id])
        if self.height-1>line_of_id:
            if len(self.matrix_of_node[line_of_id+1])-1>=index_of_id and self.matrix_of_node[line_of_id+1][index_of_id]!=None: neighboors.append(self.matrix_of_node[line_of_id+1][index_of_id])
            
        return neighboors
    
    def write_matrix_txt(self, file=1):
        """display the graph and the matrix of nodes in a file name final_output<file> where file is in parameter 
        works correctly ONLY if their is less than 1000 nodes"""
        maximum=max([len(e) for e in self.matrix_of_node])
        # this list will be the final output in severals dimension
        list_final_string=[[" " for _ in range(maximum*5)] for _ in range(len(self.matrix_of_node)*2)]
        i=0; y=0
        for line in self.matrix_of_node:
            for node in line:
                # we don't print None nodes
                if node!=None:
                    if self.name_all_graphe[node]!=None:
                        affichage=self.name_all_graphe[node]
                    else: affichage=node
                    # all nodes must be printed in 2 caracters
                    if int(affichage)<10:
                        affichage="000"+affichage
                    elif int(affichage)<100:
                        affichage="00"+affichage
                    elif int(affichage)<1000:
                        affichage="0"+affichage
                    else:
                        affichage=affichage
                    # each 3 caracters is a - if theire is a path, else there is nothing
                    # each 2 over 3 caracters are the id of the node
                    list_final_string[i][y]=affichage[0]
                    list_final_string[i][y+1]=affichage[1]
                    list_final_string[i][y+2]=affichage[2]
                    list_final_string[i][y+3]=affichage[3]
                    
                    # for each path registered in the list of all path corresponding to the node
                    # path_id correspond to the id of the other node of the path
                    for path_id in self.all_graph[node]:
                        # if the path is on the left of the node
                        if self.matrix_of_node[i//2][0] != node and self.matrix_of_node[i//2][y//5 -1] == path_id: 
                            list_final_string[i][y-1]="-"
                        # if the path is on the right of the node    
                        if self.matrix_of_node[i//2][-1] != node and self.matrix_of_node[i//2][y//5 +1] == path_id: 
                            list_final_string[i][y+4]="-"
                        # if the path is on the top of the node
                        if i>0 and len(self.matrix_of_node[i//2 -1])-1>=y//5 and self.matrix_of_node[i//2 -1][y//5]==path_id:
                            list_final_string[i-1][y+2]="|"
                        # if the path is on the bottom of the node
                        if self.height-1>i and len(self.matrix_of_node[i//2 +1])-1>=y//5 and self.matrix_of_node[i//2 +1][y//5]==path_id:
                            list_final_string[i+1][y+2]="|"
                y+=5
            i+=2;y=0
        with open(f"{self.directory}\\map\\output\\final_output{file}.txt", 'w') as f:    
            for line in list_final_string:
                f.write("".join(line))
                f.write("\n")