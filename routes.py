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
  def __init__(self, x, y, name): # location constructor
    self.coordinates = (x,y)
    self.name = name


class Population:
    candidate_list= [] 
    generation_num = 0
    candidate_selection = []

    """"constructor for a population given its length and the list
    of locations which it candidate has to go through"""
    def __init__(self,population_length,locations):
      self.n = population_length ## number of elements in the population

      for i in range(population_length): ## iterate as many times as the population length
        self.candidate_list.append(Candidate(locations,True)) ## append a new candidate object to the list

    def best_candidates(self):
      """function returns a candidate list ordered by its fitness value"""

      for dna in self.candidate_list:
        dna.get_fitnesse()
      
      return sorted(self.candidate_list,key=attrgetter('fitnesse'), reverse=True)  ######################
        
    def mutate_population(self, mutation_rate):
      mutated_population = []
      for dna in self.candidate_list:
        new_candidate = dna.mutate(mutation_rate)
        mutated_population.append(new_candidate)
      self.candidate_list = mutated_population

    def get_max_fitnesse(self):
      return self.best_candidates()[0]


      
    def selection(self, eliteSize=None):
      """La seleccion de los padres se hace en funcion del fitness de cada candidato
      Este algoritmo garantiza que todo candidato pueda elegirse pero tambien hace una seleccion ponderada segun el fitness
      el fitness dado por la funcion mejoresCandidatos determina el peso de la probabilidad a ser seleccionado basicamente"""
      ordered_candidates = self.best_candidates()

      #metodo roulette wheel
      df = pd.DataFrame([x.as_dict() for x in ordered_candidates], columns=["Route","Fitness"])
      df['cum_sum'] = df.Fitness.cumsum()
      df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
      
      if eliteSize:
        for i in range(0, eliteSize):
            self.candidate_selection.append(ordered_candidates[i])
            
        for i in range(0, len(ordered_candidates) - eliteSize):
            pick = 100*random.random()
            for i in range(0, len(ordered_candidates)):
                if pick <= df.iat[i,3]:
                    self.candidate_selection.append(ordered_candidates[i][0])
                    
                    break
      else:
        for i in range(0, len(ordered_candidates)):
          pick = 100*random.random()
          for i in range(0, len(ordered_candidates)):
            if pick <= df.iat[i,3]:
              self.candidate_selection.append(ordered_candidates[i][0])

    
    def reproduction(self):
      """ the candidates' probability to be selected depends on its'
      fitnesse value  """
      new_gen = []
      population_fitness = sum([ dna.fitnesse for dna in self.candidate_list])  #it sums up all fitnesses of the candidates of the current generation
      dna_probabilities = [(dna.fitnesse / population_fitness) for dna in self.candidate_list] #it iterates and creates a list of 
                                                                                               #all candidates and based on the total sum of
                                                                                               #the fitnesses of the population it calculates the corresponging
                                                                                               #fitness of each candidate --> candidateFitness/totalPopulationFitness

      for i in range(len(self.candidate_list)):
        
        dad = np.random.choice(self.candidate_list,p=dna_probabilities) #returns a random (but weighted choice) candidate from the list
        mom = np.random.choice(self.candidate_list,p=dna_probabilities) #the parameter p = dna_probabilities makes the random selection weighted
                                                                        #since candidates with higher fitness will have more probabilities of been chosen

        new_gen.append(mom.crossover(dad))


            
      self.candidate_list = new_gen
      self.generation_num +=1
      self.fitnesse = 0.0

      return 
      
    def plot_route(self):
      
      coordinates_list = []

      plt.ion()


      fig, ax = plt.subplots(figsize=(22, 12))
      
      img = plt.imread('mapa.png')

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
    if len(args) > 1:
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


  img = plt.imread('mapa.png')
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

def plot_best_routes(best_candidates):
      coordinates_list = []

      plt.ion()


      fig, ax = plt.subplots(figsize=(22, 12))      
      img = plt.imread('mapa.png')



      for dna in best_candidates:
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

  for r in routes:
    list.append(Location(r['Coordinates'][0],r["Coordinates"][1],r['Name']))

  population = Population(population_size,list)


  for i in range(max_generations):
    print(population.get_max_fitnesse().fitnesse)
    
    population.selection()
    population.reproduction()
    population.mutate_population(mutation_rate)

    generations.append(population.get_max_fitnesse())

  plot_best_routes(generations)

routes = [
    {"Name": 'Abiyán', "Coordinates": [200,740]}, 
    {"Name": "Niger", "Coordinates": [320,950]},
    {"Name": "Namibia", "Coordinates": [400,200]},
    {"Name": "Congo", "Coordinates": [450,600]}, 
    {"Name": "Ruanda", "Coordinates": [500,600]}, 
    {"Name": "Zambia", "Coordinates": [460,400]},
    {"Name": "Madagascar", "Coordinates": [650,300]},
    {"Name": "Sudán", "Coordinates": [500,900]},    
    {"Name": "Hyberabad", "Coordinates": [920,920]}
]

list =[]

geneticAlgorithm(routes, 100, 100, 0.01)
