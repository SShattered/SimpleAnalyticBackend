import threading

import TcpServer


def main():
    # First we start our TCP Server
    tcpServer = TcpServer.TcpServer("0.0.0.0", 9999)
    tcpServer.listen()

if __name__=="__main__":
    main()