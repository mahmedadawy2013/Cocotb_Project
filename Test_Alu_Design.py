#******************************************************************************
# *
# * Module: Private - Test bench For Arithmatic Logic Unit ' ALU ' Block Using
# * Cocotb
# *
# * File Name: ALU_Test.py
# *
# * Description:  this file is used for Testing the Arithmatic Logic Unit
# *               Block , ALU is the fundamental building block of the processor
# *               which is responsible for carrying out the arithmetic, logic functions
# *
# * Author: Mohamed A. Eladawy
# *
# *******************************************************************************/
import cocotb
from cocotb import queue
from cocotb.triggers import *
from cocotb_bus.drivers import *
from cocotb_coverage.crv import *
from cocotb_coverage.coverage import *
from cocotb.result import TestError,TestSuccess
from queue import Queue
import cocotb.queue
import queue
import random

#Coverage groub To Check We Have Covered All Input Data To The Module Design
Coverage = coverage_section(
CoverPoint("top.a"  , vname="a"  , bins=list(range(0, 16))) ,
CoverPoint("top.b"  , vname="b"  , bins=list(range(0, 16))) ,
CoverPoint("top.op" , vname="op" , bins=list(range(0, 4)))  ,
CoverCross("top.all_cases" , items=["top.a","top.b","top.op"])
)
@Coverage
def sample (a, b, op):
    cocotb.log.info("[Coverage SampLe] The randomized values are a= "+ bin(int(a))+ " b= " +bin(int(b)) + " op= " +bin(int(op)))


# This is the base transaction object Container that will be used
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
       self.queue = []
       self.driver_done1 = Event(name=None)
   async def Generato_Run_Task (self):
      for loob_variable in range(9000):
         self.driver_done1.clear()
         self.trans_item_sent.randomize()
         cocotb.log.info("[Generator] Loop: create next item  " + str(loob_variable))
         sample(self.trans_item_sent.a,self.trans_item_sent.b ,self.trans_item_sent.op)
         self.queue.append(self.trans_item_sent)
         cocotb.log.info("[Generator] Sending To The Driver..... ")
         cocotb.log.info("[Generator] Wait for driver to be done " )
         await self.driver_done1.wait()


class driver :
   queue = []
   event_driver  = Event (name=None)
   event_monitor = Event (name=None)
   def __int__(self,name = "DRIVER"):
      self.name = name
      self.queue = []
      self.trans_item_reciever = transactions()
   async def Driver_Run_Task (self,dut_driver):
      while(self.queue):
         self.event_driver.clear()
         cocotb.log.info("[Driver] waiting for item ...")
         self.trans_item_reciever = self.queue.pop(0)
         cocotb.log.info("[Driver] Recieved items is  ...")
         self.trans_item_reciever.print()
         cocotb.log.info("[Driver] Driver Is Sending To Dut Module Now ...")
         dut_driver.a.value  = self.trans_item_reciever.a
         dut_driver.b.value  = self.trans_item_reciever.b
         dut_driver.op.value = self.trans_item_reciever.op
         self.event_monitor.set()
         self.event_driver.set()
         await Timer(10, units="ns")


class monitor :
   trans_item_monitor = transactions()
   queue1 = cocotb.queue.Queue()
   def __int__(self,name = "MONITOR"):
      self.name = name
      self.trans_item_monitor = transactions()
      self.monitor_done = Event(name = None)
   async def Monitor_Run_Task (self,dut_monitor) :
      while(True):
         self.monitor_done.clear()
         await Timer(1, units="ns")
         cocotb.log.info("[Monitor] waiting for item ...")
         self.trans_item_monitor.a   = dut_monitor.a
         self.trans_item_monitor.b   = dut_monitor.b
         self.trans_item_monitor.c   = dut_monitor.c
         self.trans_item_monitor.op  = dut_monitor.op
         self.trans_item_monitor.out = dut_monitor.out
         await self.queue1.put(self.trans_item_monitor)
         cocotb.log.info("[Monitor] Item Has Been Recieved From Dut Module ...")
         self.trans_item_monitor.print()
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
      self.queue2 = []
      self.drv_box = queue.Queue()
      self.score_board_event = Event (name = None)
   async def Score_Board_Run_Task (self) :
      cocotb.log.info("[Score Board] insideeeeeeeeeeeeeeeee ...")
      while (True):
         cocotb.log.info("[Score Board] waiting for item ...")
         self.test_item = await self.drv_box.get()
         self.golden_item.Copy_Items(self.test_item)
         cocotb.log.info("[Score Board] Recieved items is  ...")
         self.test_item.print()
         if (str(self.test_item.op) == str("00")) :
            self.index = int((str(self.test_item.a) + str(self.test_item.b) + str(self.test_item.op)))
            self.Binary_Golden_item = bin ( int (self.golden_item.a) + int (self.golden_item.b) )[2:].zfill(5)
            cocotb.log.info("***************************** Printing Depuging Elements ***************************** ")
            cocotb.log.info(self.Binary_Golden_item)
            self.Binary_Golden_item_C = str(self.Binary_Golden_item[0])
            cocotb.log.info(self.Binary_Golden_item_C)
            self.Binary_Golden_item_Out = str(self.Binary_Golden_item[1:])
            cocotb.log.info(self.Binary_Golden_item_Out)
            if ((self.Binary_Golden_item_Out != str(self.test_item.out))  or (self.Binary_Golden_item_C != str (self.test_item.c) )) :
               cocotb.log.info("*************************** Test Case Adding Hase Failed *************************** ")
               self.Bugs_List.append(self.index)
               cocotb.log.info("Expected Output and Carry is : ")
               cocotb.log.info(self.Binary_Golden_item_Out )
               cocotb.log.info(self.Binary_Golden_item_C)
               self.num_failure = self.num_failure+1
            else:
               cocotb.log.info("*************************** Test Case Adding Hase succeeded *************************** ")
               self.num_passes = self.num_passes + 1

         elif (str(self.test_item.op) == str("01")) :
            self.index = int((str(self.test_item.a) + str(self.test_item.b) + str(self.test_item.op)))
            self.Binary_Golden_item = bin ( int (self.golden_item.a) ^ int (self.golden_item.b) )[2:].zfill(5)
            cocotb.log.info("***************************** Printing Depuging Elements ***************************** ")
            cocotb.log.info(self.Binary_Golden_item)
            self.Binary_Golden_item_C = str(self.Binary_Golden_item[0])
            cocotb.log.info(self.Binary_Golden_item_C)
            self.Binary_Golden_item_Out = str(self.Binary_Golden_item[1:])
            cocotb.log.info(self.Binary_Golden_item_Out)
            if ((self.Binary_Golden_item_Out != str(self.test_item.out))  or (self.Binary_Golden_item_C != str (self.test_item.c) )) :
               cocotb.log.info("*************************** Test Case Xor Hase Failed **************************** ")
               self.Bugs_List.append(self.index)
               cocotb.log.info("Expected Output and Carry is : ")
               cocotb.log.info(self.Binary_Golden_item_Out )
               cocotb.log.info(self.Binary_Golden_item_C)
               self.num_failure = self.num_failure+1
            else:
               cocotb.log.info("*************************** Test Case Xor Hase succeeded *************************** ")
               self.num_passes = self.num_passes + 1


         elif (str(self.test_item.op) == str("10")) :
            self.index = int((str(self.test_item.a) + str(self.test_item.b) + str(self.test_item.op)))
            self.Binary_Golden_item = bin ( int (self.golden_item.a) & int (self.golden_item.b) )[2:].zfill(5)
            cocotb.log.info("***************************** Printing Depuging Elements ***************************** ")
            cocotb.log.info(self.Binary_Golden_item)
            self.Binary_Golden_item_C = str(self.Binary_Golden_item[0])
            cocotb.log.info(self.Binary_Golden_item_C)
            self.Binary_Golden_item_Out = str(self.Binary_Golden_item[1:])
            cocotb.log.info(self.Binary_Golden_item_Out)
            if ((self.Binary_Golden_item_Out != str(self.test_item.out))  or (self.Binary_Golden_item_C != str (self.test_item.c) )) :
               cocotb.log.info("*************************** Test Case Anding Hase Failed *************************** ")
               self.Bugs_List.append(self.index)
               cocotb.log.info("Expected Output and Carry is : ")
               cocotb.log.info(self.Binary_Golden_item_Out )
               cocotb.log.info(self.Binary_Golden_item_C)
               self.num_failure = self.num_failure+1
            else:
               cocotb.log.info("*************************** Test Case Anding Hase succeeded *************************** ")
               self.num_passes = self.num_passes + 1


         elif (str(self.test_item.op) == str("11")) :
            self.index = int((str(self.test_item.a) + str(self.test_item.b) + str(self.test_item.op)))
            self.Binary_Golden_item = bin ( int (self.golden_item.a) | int (self.golden_item.b) )[2:].zfill(5)
            cocotb.log.info("***************************** Printing Depuging Elements ***************************** ")
            cocotb.log.info(self.Binary_Golden_item)
            self.Binary_Golden_item_C = str(self.Binary_Golden_item[0])
            cocotb.log.info(self.Binary_Golden_item_C)
            self.Binary_Golden_item_Out = str(self.Binary_Golden_item[1:])
            cocotb.log.info(self.Binary_Golden_item_Out)
            if ((self.Binary_Golden_item_Out != str(self.test_item.out))  or (self.Binary_Golden_item_C != str (self.test_item.c) )) :
               cocotb.log.info("*************************** Test Case Or Hase Failed *************************** ")
               self.Bugs_List.append(self.index)
               cocotb.log.info("Expected Output and Carry is : ")
               cocotb.log.info(self.Binary_Golden_item_Out )
               cocotb.log.info(self.Binary_Golden_item_C)
               self.num_failure = self.num_failure+1
            else:
               cocotb.log.info("***************************** Test Case Or Hase succeeded ***************************** ")
               self.num_passes = self.num_passes + 1
               cocotb.log.info("Expected Output and Carry is : ")
               cocotb.log.info(self.Binary_Golden_item_Out )
               cocotb.log.info(self.Binary_Golden_item_C)

class environment :
   g = Generator()
   d = driver()
   m = monitor()
   queue = []
   def __int__(self,name = "ENVIRONMENT"):
      self.name = name
      self.g = Generator()
      self.d = driver()
      self.m = monitor()
      self.queue = []
      self.drv_done = Event (name = None)
   async def Environment_Run_Task (self,dut_env) :
      self.g.queue   = self.d.queue
      self.g.driver_done1 = self.d.event_driver
      self.m.monitor_done = self.d.event_monitor
      cocotb.start_soon(self.g.Generato_Run_Task())
      cocotb.start_soon(self.d.Driver_Run_Task(dut_env))
      cocotb.start_soon(self.m.Monitor_Run_Task(dut_env))

class Test :
   s = scoreboard ()
   e = environment ()
   def __int__(self,name = "TEST"):
      self.name = name
      self.s = scoreboard()
      self.e = environment()
   async def Test_Run_Task(self,dut_test):
      self.s.drv_box = self.e.m.queue1
      cocotb.start_soon(self.e.Environment_Run_Task(dut_test))
      cocotb.start_soon(self.s.Score_Board_Run_Task())
@cocotb.test()
async def Test_Alu_Design(dut):
   cocotb.log.info(" WE ARE STARTING THE SIMULATION ")
   t = Test()
   cocotb.start_soon(t.Test_Run_Task(dut))
   await Timer(9000000, units="ns")
   my_Unique_List = set(t.s.Bugs_List)
   cocotb.log.info("******************************* simulation Finished **********************************")
   cocotb.log.info("NUMBER OF TEST CASES WHICH HAS PASSED is : " + str(t.s.num_passes))
   cocotb.log.info("NUMBER OF TEST CASES WHICH HAS Failed is : " + str(t.s.num_failure))
   cocotb.log.info("NUMBER OF UNIQUE BUGS OF THE DESIGN IS   : " + str(len(my_Unique_List)))
   coverage_db.export_to_xml(filename="ALU_coverage.xml")