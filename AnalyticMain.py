import TcpServer


def main():
    tcpServer = TcpServer.TcpServer("0.0.0.0", 9999)
    tcpServer.listen()

if __name__=="__main__":
    main()