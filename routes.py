import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np  # sample data
import random
import math
from operator import attrgetter
from sklearn import preprocessing
import pandas as pd

class Location:
  """ class that represents a given location determined by
   its name and (x,y) coordinates
  """
  def __init__(self, x, y): # location constructor
    self.coordinates = (x,y)

class Population:
    candidate_list= [] 
    generation_num = 0

    """"constructor for a population given its length and the list
    of locations which it candidate has to go through"""
    def __init__(self,population_length,locations):
      self.n = population_length ## number of elements in the population

      for i in range(population_length): ## iterate as many times as the population length
        self.candidate_list.append(Candidate(locations,True)) ## append a new candidate object to the list, True determines that is first generation

    def best_candidates_list(self):
      """function returns a candidate list ordered by its fitness value"""

      for dna in self.candidate_list:
        dna.get_fitnesse()
      
      return sorted(self.candidate_list,key=attrgetter('fitnesse'), reverse=True)  ######################
        
    def mutate_population(self, mutation_rate):
      """function that iterates for each element of the population and invokes
      the mutate function """

      mutated_population = []
      for dna in self.candidate_list:
      
        new_candidate = dna.mutate(mutation_rate) # invoke mutate function for that element
        mutated_population.append(new_candidate) # append to the mutated population the returned element

      self.candidate_list = mutated_population # replace population with the mutated one generated

    def get_max_fitnesse(self):
      """function that returns the element with the max fitnesse of the population"""
      return self.best_candidates_list()[0]

    
    def get_min_fitnesse(self):
      """function that returns the element with the min fitnesse of the population"""
      return self.best_candidates_list()[len(self.candidate_list)-1]
      
    def selection(self):
      """function that returns an element chosen with the accept reject-algorithm"""
    
      while(True):
        partner = {}

        random_index = random.randint(0,len(self.candidate_list)-1) #pick a random index
        partner = self.candidate_list[random_index] # get the element at that index

        random_fitness = random.uniform(self.get_min_fitnesse().fitnesse,self.get_max_fitnesse().fitnesse) # pick a random fitnesse between the min and max

        if( random_fitness < partner.fitnesse): # if the fitnesse of the element selected is greater than the random fitnesse picked
          return partner #return element

          


    
    def reproduction(self):
      """ function that iterates through the number of elements of the population
      and picks two parents to generate a child through the crossover function  """
      new_gen = []

      for i in range(len(self.candidate_list)):
        
        # invokes selection function to choose mother and father
        dad = self.selection() 
        mom = self.selection() 

        new_gen.append(mom.crossover(dad)) # invoke 


            
      self.candidate_list = new_gen # assign the new generation created to the population list 
      self.generation_num +=1 # increase number of generations

      return 
      
    def plot_route(self):
      
      coordinates_list = []

      plt.ion()


      fig, ax = plt.subplots(figsize=(22, 12))
      
      img = plt.imread('mapa_catar.png')

      for dna in self.candidate_list:
        for location in dna.route:
          coordinates_list.append(location.coordinates)
      
      routes = np.array(coordinates_list)  
      # create an array with coordinates and not location names which is what is needed to plot it

      x,y = routes.T


      sns.scatterplot(x=x,y=y,ax=ax,marker='x',color='red',s=200)
      # plot locations with an 'x' marker
      plt.xlim(0, 1000)
      plt.ylim(0, 1000)

      ax.xaxis.set_visible(False)
      ax.yaxis.set_visible(False)

      ax.imshow(img, extent=[0, 1000, 0, 1000], aspect='auto')
      plt.draw()

      colors = []

      for i in range(len(self.candidate_list)):
        colors.append('#%06X' % random.randint(0, 0xFFFFFF))



      for dna in self.candidate_list:
        routes = []
        coordinates_list = []
        plt.draw()

        for location in dna.route:
          coordinates_list.append(location.coordinates)
       
        routes = np.array(coordinates_list)  
        # create an array with coordinates and not location names which is what is needed to plot it

        x,y = routes.T
        

        plt.plot(x,y,linestyle='dotted', color=colors[self.candidate_list.index(dna)])
        
        # plot lines between locations to visualize routes
        # separate x and y coordinates


        fig.canvas.draw_idle()
        plt.pause(1)

      plt.waitforbuttonpress()



class Candidate:
  """class for a candidate (solution). For this solution, a candidate represents an specific route, 
      it goes through all locations only once and it must visit all of them"""

  route = []
  fitnesse= 0.0

  def as_dict(self):
        return {'Route': self.route, 'Fitnesse': self.fitnesse}
  

  def __init__(self, *args):
    #if first generation, we create a random route
    if len(args) > 1: #if first generation we have an extra boolean parameter 'True'
      self.route= []
      num=0
      random_list=[] # create list from which the dna is going to choose which location to visit next 

      list_locations = args[0]
      

      for num in range(len(list_locations)):
          random_list.append(num) # create list with numbers from 0 to the length of the list of locations the dna has to visit

      
      for i in range(len(list_locations)): 
        random_num = random.choice(random_list) # pick randomly a number from the list created
        self.route.append(list_locations[random_num]) # select the next location the dna will visit which is the one whose index equals the random number picked
        random_list.remove(random_num) # remove the random number picked from the list in order to avoid selecting twice the same location

    else:
      self.route = args[0]
    

  def get_fitnesse(self):
    """returns the fitness of a candidate based on the route total distance"""
    if self.fitnesse == 0.0:
      distance = 0

      # [0,1,2,3,4] ------> [0 vs 1, 1 vs 2, 2 vs 3, 3 vs 4]
      for index in range(len(self.route)-1):
        dna_a = self.route[index] 
        dna_b = self.route[index+1]

        route_dist = math.dist(dna_a.coordinates,dna_b.coordinates) # calculate euclidian distance from pitagoras theorem
        distance += route_dist   # add to the distance value the distance from the dna_a and dna_b picked in this iteration
      
      self.fitnesse =  1/(distance)
      return self.fitnesse
    
    else:
      return self.fitnesse
  
  def crossover(self, partner):
    """Function crossover. It takes the genes from two parents to create a child
    Basicaly, the function takes a piece of one solution, and another one from the other solution in order to mix both in the child
    """
    #we randomly decide what portion of the child will take the adn of the 'mom' 
    #the other portion left will be filled with the 'dad' adn
    adn1 = int(random.random() * len(self.route))
    adn2 = int(random.random() * len(self.route))
    
    startGene = min(adn1, adn2)
    endGene = max(adn1, adn2)
    mom = []
    for i in range(startGene, endGene):
        mom.append(self.route[i])
        
    dad = [item for item in partner.route if item not in mom]
    child = Candidate(mom + dad)#new solution produeced by both parents

    return child
    
  def mutate(self,mutationRate):
    for i in range(len(self.route)): #recorro las casas y si toca intercambiarintercambia
      if(random.random() < mutationRate): #queremos que el mutationRate sea bajo para que sea baja la probabilidad de mutar
          index_change = int(random.random() * len(self.route)) #aleatoriamente agarra la casa por la que va a intercambiarse
          # ejemplo:
          #>>> camino = [1,2,3,4,5,6,7,8]
          #>>> int(random.random() * len(camino)) 
          # 6
          #>>> int(random.random() * len(camino))
          # 4
          location1 = self.route[i] #intercambio las casas
          location2 = self.route[index_change]
          self.route[i] = location2
          self.route[index_change] = location1
    return self
    
  

def plot_route(route):

  coordinates = []
  for c in route:
      coordinates.append(c.coordinates)

  routes = np.array(coordinates)  
  # create an array with coordinates and not location names which is what is needed to plot it

  x,y = routes.T
  # separate x and y coordinates


  img = plt.imread('mapa_catar.png')
  fig, ax = plt.subplots(figsize=(22, 12))

  sns.scatterplot(x=x,y=y,ax=ax,marker='x',color='red',s=200)
  # plot locations with an 'x' marker
  plt.xlim(0, 1000)
  plt.ylim(0, 1000)

  ax.xaxis.set_visible(False)
  ax.yaxis.set_visible(False)

  ax.imshow(img, extent=[0, 1000, 0, 1000], aspect='auto')

  plt.plot(x,y,linestyle='dotted', color='black')
  # plot lines between locations to visualize routes

  plt.show()

def plot_best_routes(best_route_each_gen):
    

      ####ploting interactive map
      coordinates_list = []

      plt.ion()


      fig, ax = plt.subplots(figsize=(22, 12))      
      img = plt.imread('mapa_catar.png')
      i=0


      for dna in best_route_each_gen:
        routes = []
        coordinates_list = []

        plt.draw()
        plt.cla()

        
        for location in dna.route:
          coordinates_list.append(location.coordinates)
       
        routes = np.array(coordinates_list)  
        # create an array with coordinates and not location names which is what is needed to plot it

        x,y = routes.T

        sns.scatterplot(x=x,y=y,ax=ax,marker='x',color='red',s=200)
        # plot locations with an 'x' marker
        plt.xlim(0, 1000)
        plt.ylim(0, 1000)

        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        ax.text(50,-50,"Generation: "+str(i))
        ax.text(50,-75,"Max fitness value: "+str(round(dna.fitnesse,7)))
        i+=1

        ax.imshow(img, extent=[0, 1000, 0, 1000], aspect='auto')
        plt.draw()

        

        plt.plot(x,y,linestyle='dotted', color='black')
        
        # plot lines between locations to visualize routes
        # separate x and y coordinates


        fig.canvas.draw_idle()
        plt.pause(0.01)

      plt.waitforbuttonpress()


def geneticAlgorithm(routes, max_generations, population_size, mutation_rate):
  generations = []
  best_fitness_each_generation= []
  for r in routes:
    list.append(Location(r['Coordinates'][0],r["Coordinates"][1]))

  population = Population(population_size,list)

  progress = []
  
  for i in range(max_generations):
      progress.append(population.get_max_fitnesse().fitnesse)
      print(population.get_max_fitnesse().fitnesse)
      
      population.selection()
      population.reproduction()
      population.mutate_population(mutation_rate)

      generations.append(population.get_max_fitnesse())
  

  ###ploting progress curve
  plt.plot(progress, label='fitness progretion per generation')
  plt.ylabel('Fitness')
  plt.xlabel('Generation')
  plt.legend
  plt.show()
  
  plot_best_routes(generations)


# routes = [
#     {"Name": 'Abiyán', "Coordinates": [200,740]}, 
#     {"Name": "Niger", "Coordinates": [320,950]},
#     {"Name": "Namibia", "Coordinates": [400,200]},
#     {"Name": "Congo", "Coordinates": [450,600]}, 
#     {"Name": "Ruanda", "Coordinates": [500,600]}, 
#     {"Name": "Zambia", "Coordinates": [460,400]},
#     {"Name": "Madagascar", "Coordinates": [650,300]},
#     {"Name": "Sudán", "Coordinates": [500,900]},    
#     {"Name": "Hyberabad", "Coordinates": [920,920]},
#      {"Name": 'Senegal', "Coordinates": [118,882]}, 
#      {"Name": "Guinea-Bisau", "Coordinates": [109,823]},
#      {"Name": "Burkina Faso", "Coordinates": [235,850]},
#      {"Name": "Benim", "Coordinates": [260,805]}, 
#      {"Name": "Nigeria", "Coordinates": [315,795]}, 
#      {"Name": "Camerún", "Coordinates": [347,705]},
#      {"Name": "Angola", "Coordinates": [385,370]},
#      {"Name": "Botsuana", "Coordinates": [450,225]},    
#      {"Name": "Sudáfrica", "Coordinates": [445,100]},
#      {"Name": 'Etiopía', "Coordinates": [580,730]}, 
#      {"Name": "Yemen", "Coordinates": [675,910]},
#      {"Name": "Omán", "Coordinates": [715,945]},
#      {"Name": "Somalía", "Coordinates": [638,703]}, 
#      {"Name": "Kenia", "Coordinates": [570,610]}, 
#      {"Name": "Tanzania", "Coordinates": [550,495]},
#      {"Name": "Mozambique", "Coordinates": [575,390]},
#      {"Name": "Zimambue", "Coordinates": [490,280]},    
#      {"Name": "Congo", "Coordinates": [375,595]},
# ]
routes = []

for i in range(30):
  routes.append({"Coordinates": [random.randint(0,1000), random.randint(0,1000)]})

list =[]

geneticAlgorithm(routes, 100, 300, 0.02)