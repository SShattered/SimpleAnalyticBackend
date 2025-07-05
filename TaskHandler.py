from Models import TaskModel
import threading 
import Analytics
import socket

class TaskHandler(object):
    threadList = []
    taskList: list[TaskModel] = []

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TaskHandler, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        print(f"Task Handler Initiated...")

    def addTask(self, task: TaskModel) -> str:
        try:
            if self.__taskExists(task) == False:
                self.taskList.append(task)
            return ""
        except Exception as e:
            return e
        
    def __taskExists(self, task: TaskModel) -> bool:
        for item in self.taskList:
            if item.Id == task.Id:
                return True
        return False
    
    def isThreadRunning(self, taskId: str) -> bool:
        for t in self.threadList:
            if t.name == taskId and t.is_alive() == True:
                return True
        return False
    
    def __removeInactiveThreads(self) -> None:
        for t in self.threadList:
            if not t.is_alive():
                t.handled = True
        self.threadList = [t for t in self.threadList if not t.handled]
    
    def runAnalytic(self, taskId: str, client_socket: socket.socket, writeMessage) -> bool:
        try:
            for task in self.taskList:
                if task.Id == taskId:
                    aThread = Analytics.Analytics(task=task, client_socket=client_socket, writeMessage=writeMessage)
                    aThread.name = task.Id
                    self.threadList.append(aThread)
                    aThread.start()
            return True
        except Exception as e:
            print(e)
            return False    

    def stopAnalytic(self, taskId: str) -> bool:
        try:
            for t in self.threadList:
                if t.name == taskId:
                    t.stop()
                    t.join()
                    break
            self.__removeInactiveThreads()
            return True
        except Exception as e:
            print(e)
            return False    

