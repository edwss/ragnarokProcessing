package main

import (
	"bufio"
	"fmt"
	"net"
)

const BUFFERSIZE = 1024

func main() {
	connection, err := net.Dial("tcp", "10.0.0.116:27001")
	if err != nil {
		panic(err)
	}
	defer connection.Close()
	fmt.Println("Connected to server")
	fmt.Println(bufio.NewReader(connection).ReadString('\n'))

}
