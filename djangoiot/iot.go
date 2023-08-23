package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Starting golang")
	for {
		select {
		case <-time.Tick(time.Second * 5):
			fmt.Println("timeout")
		}
	}
}
