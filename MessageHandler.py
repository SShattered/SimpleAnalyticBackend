import json
import threading
import socket
from Models import MessageModel
from Models import TaskModel
from dataclasses import asdict

import TaskHandler

class MessageHandler:
    def __init__ (self, writeString) -> None:
        self.taskHandler: TaskHandler.TaskHandler
        self.taskHandler = TaskHandler.TaskHandler()
        self.sendMessage = writeString
        print("Message Handler Initiated...")

    def handleMessages(self, message, client_socket: socket.socket) -> None:
        json_data = json.loads(message)
        inc = json_data.get("Instruction")

        if(inc is None):
            print("Invalid message")
            return
        match inc:
            # check if the task exists. if not add task
            # check if it's running or stopped
            # send back status
            case "Sync":
                self.syncTask(client_socket, json_data)

            case "Start":
                self.startTask(client_socket, json_data)

            case "Stop":
                self.stopTask(client_socket, json_data)

            case _:
                print ("")

    def test(self, func, value):
        return func(value)
    
    def syncTask(self, client_socket: socket.socket, json_data) -> None:
        inc = "Sync"
        msgId = json_data.get("MessageId")
        msg = json_data.get("Message")

        myTask: TaskModel = TaskModel(**msg)
        result = self.taskHandler.addTask(myTask)
        if result == "":
            if self.taskHandler.isThreadRunning(myTask.Id) == True:
                self.__writeMessage(msgId, client_socket, inc, "Running")
            else:
                self.__writeMessage(msgId, client_socket, inc, "Stopped")
        else:
            self.__writeMessage(msgId, client_socket, inc, "error")

    def startTask(self, client_socket: socket.socket, json_data) -> None:
        inc = "Start"
        msgId = json_data.get("MessageId")
        taskId = json_data.get("Message")

        result = self.taskHandler.runAnalytic(taskId, client_socket, self.__writeMessage)
        if result == True:
            self.__writeMessage(msgId, client_socket, inc, "Started")
        else:
            self.__writeMessage(msgId, client_socket, inc, "Failed")

    def stopTask(self, client_socket: socket.socket, json_data) -> None:
        inc = "Stop"
        msgId = json_data.get("MessageId")
        msg = json_data.get("Message")
    
        result = self.taskHandler.stopAnalytic(msg)
        if result == True:
            self.__writeMessage(msgId, client_socket, inc, "Stopped")
        else:
            self.__writeMessage(msgId, client_socket, inc, "Failed")

    def __writeMessage(self, msgId: str, client_socket: socket.socket, inc: str, message: str) -> None:
        messageModel = MessageModel(msgId, inc, message)
        data_dict = asdict(messageModel)
        json_string_response = json.dumps(data_dict)
        #print(json_string_response)
        self.sendMessage(json_string_response, client_socket)
