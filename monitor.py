#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucianavarromartin
"""

from multiprocessing import Process, \
  BoundedSemaphore, Semaphore, Lock, Condition,\
  current_process, \
  Value, Array, Manager
from time import sleep
from random import random

#Cada filosofo sólo puede comer si los filosofos de al lado no tienen bloqueado
#ningún tenedor.
#INVARIANTE: {para todo i : phil[i]->(not(phil[i-1]) y not(phil[i+1]))}

class Table():
    def __init__(self, nphil: int, manager):
        self.mutex = Lock()
        self.nphil = nphil
        self.manager = manager
        self.phil = self.manager.list([False]* nphil)
        # Es una variable compartida: False si phil[i] no está comiendo
        self.eating=Value('i',0)
        self.current_phil = None # El que está comiendo ahora
        self.free_fork= Condition(self.mutex) #Variable de condición
        
        
    def set_current_phil(self, i):
        self.current_phil = i
        
    #Para verificar si los filosofos de al lado están comiendo
    def no_comen_lados(self):
        """
        función auxiliar para poder ejecutar la variable de condición
        en la función wants_eat. Si la hubieramos puesto directamente
        entre los paréntesis de self.free_fork.wait_for() hubiera adquirido 
        un valor fijo todo el rato y no funcionaría bien.
        """
        n = self.current_phil
        return (not self.phil[(n-1)%(self.nphil)]) and (not self.phil[(n+1)%(self.nphil)])
    
   
    def wants_eat(self, i):
        """
        El filosofo i quiere comer, para poder hacerlo, primero hay que ver
        si los filosofos i-1 y i+1 están comiendo o no.
        En el caso de que uno de los dos o los dos están comiendo, espera a 
        a poder comer.
        """
        self.mutex.acquire()
        self.current_phil = i
        self.free_fork.wait_for(self.no_comen_lados)
        #Espera a que los de los lados dejen los tenedores
        self.phil[i]=True
        #Avisa a la variable compartida de que el filosofo i está comiendo
        self.eating.value+=1
        self.mutex.release()
        
    
    def wants_think(self,i):
        """
        El filosofo i quiere dejar de comer y ponerse a pensar. 
        Hay que avisar para que los que estén a su lado y quieran comer puedan
        hacerlo.
        """
        self.mutex.acquire()
        self.phil[i]=False
        #Avisa a la variable compartida de que el filosofo num ha dejado
        #los tenedores
        self.eating.value-=1
        self.free_fork.notify()
        #Avisa a la variable de condición para ver si hay algun filosofo que
        #está esperando a comer al lado del filosofo num, y ya puede, por que
        # este ha dejado los tenedores
        self.mutex.release()
        

