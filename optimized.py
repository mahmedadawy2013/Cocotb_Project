import cocotb
from cocotb import queue
import logging
from cocotb.triggers import *
from cocotb_coverage.crv import *
from cocotb_coverage.coverage import *
from cocotb.result import TestError,TestSuccess
from queue import Queue
import cocotb.queue
import queue
import random
# queue1 = cocotb.queue.Queue()

class transactions(Randomized):
   def __init__(self ,name = "TRANSACTIONS"):
      Randomized.__init__(self)
      self.name = name
      self.a   = 0
      self.b   = 0
      self.op  = 0
      self.c   = 0
      self.out = 0
      self.add_rand("a" , list(range(0, 16)))
      self.add_rand("b" , list(range(0, 16)))
      self.add_rand("op", list(range(0, 4 )))
   def Generate_Values (self):
      self.a   = random.randrange(0,16)
      self.b   = random.randrange(0,16)
      self.op  = random.randrange(0,4)
   def print (self):
      cocotb.log.info("the Value of a is   " + str(self.a  ))
      cocotb.log.info("the Value of b is   " + str(self.b  ))
      cocotb.log.info("the Value of c is   " + str(self.c  ))
      cocotb.log.info("the Value of op is  " + str(self.op ))
      cocotb.log.info("the Value of out is " + str(self.out))
   def Copy_Items (self,transaction_object):
      self.a   = transaction_object.a
      self.b   = transaction_object.b
      self.c   = transaction_object.c
      self.op  = transaction_object.op
      self.out = transaction_object.out

class Generator :

   def __init__(self, name="GENERATOR"):
       self.name = name
       self.trans_item_sent = transactions()
       self.queue = cocotb.queue.Queue()
       self.driver_done1 = Event(name=None)
   async def Generato_Run_Task (self):
      for loob_variable in range(10):
         # self.driver_done1.clear()
         self.trans_item_sent.randomize()
         cocotb.log.info("[Generator] Loop: create next item  " + str(loob_variable))
         await self.queue.put(self.trans_item_sent)
         cocotb.log.info("[Generator] Sending To The Driver..... ")
         cocotb.log.info("[Generator] Wait for driver to be done " )
         await Timer(5, units="ns")
         # await self.driver_done1.wait()

class driver :
   queue1 = cocotb.queue.Queue()
   event_monitor = Event(name=None)
   def __int__(self,name = "DRIVER"):
      self.name = name
      self.queue1 = cocotb.queue.Queue()
      self.trans_item_reciever = transactions()
   async def Driver_Run_Task (self,dut_driver):
      while(True):
         # self.event_driver.clear()
         cocotb.log.info("[Driver] waiting for item ...")
         self.trans_item_reciever = await self.queue1.get()
         cocotb.log.info("[Driver] Recieved items is  ...")
         self.trans_item_reciever.print()
         cocotb.log.info("[Driver] Driver Is Sending To Dut Module Now ...")
         dut_driver.a.value  = self.trans_item_reciever.a
         dut_driver.b.value  = self.trans_item_reciever.b
         dut_driver.op.value = self.trans_item_reciever.op
         self.event_monitor.set()


class monitor :
   trans_item_monitor = transactions()
   queuem = cocotb.queue.Queue()
   monitor_done = Event(name=None)
   def __int__(self,name = "MONITOR"):
      self.name = name
      self.trans_item_monitor = transactions()
      self.monitor_done = Event(name = None)
   async def Monitor_Run_Task (self,dut_monitor) :
      while(True):
         self.monitor_done.clear()
         await Timer(3, units="ns")
         cocotb.log.info("[Monitor] waiting for item ...")
         self.trans_item_monitor.a   = dut_monitor.a
         self.trans_item_monitor.b   = dut_monitor.b
         self.trans_item_monitor.c   = dut_monitor.c
         self.trans_item_monitor.op  = dut_monitor.op
         self.trans_item_monitor.out = dut_monitor.out
         await self.queuem.put(self.trans_item_monitor)
         cocotb.log.info("[Monitor] Item Has Been Recieved From Dut Module ...")
         self.trans_item_monitor.print()
         await Timer(1, units="ns")
         await self.monitor_done.wait()

class scoreboard :
   test_item = transactions()
   golden_item = transactions()
   num_passes = 0
   num_failure = 0
   drv_box = cocotb.queue.Queue()
   Bugs_List = []
   def __int__(self,name = "SCOREBOARD"):
      self.name = name
      self.index = 0
      self.test_item   = transactions()
      self.golden_item = transactions ()
      self.Binary_Golden_item = 0b0
      self.Binary_Golden_item_C = 0
      self.Binary_Golden_item_Out = 0
      self.num_passes  = 0
      self.num_failure = 0
      self.drv_box = cocotb.queue.Queue()
      self.score_board_event = Event (name = None)
   async def Score_Board_Run_Task (self) :
      cocotb.log.info("[Score Board] insideeeeeeeeeeeeeeeee ...")
      while (True):
         cocotb.log.info("[Score Board] waiting for item ...")
         self.test_item = await self.drv_box.get()
         self.golden_item.Copy_Items(self.test_item)
         cocotb.log.info("[Score Board] Recieved items is  ...")
         self.test_item.print()
@cocotb.test()
async def Test_Alu_Design(dut):
   cocotb.log.info(" WE ARE STARTING THE SIMULATION ")
   g = Generator()
   d = driver()
   m = monitor()
   s = scoreboard()
   s.drv_box = m.queuem
   g.queue = d.queue1
   d.event_monitor = m.monitor_done
   cocotb.start_soon(g.Generato_Run_Task())
   cocotb.start_soon(d.Driver_Run_Task(dut))
   cocotb.start_soon(m.Monitor_Run_Task(dut))
   cocotb.start_soon(s.Score_Board_Run_Task())
   await Timer(1000 , units="ns")