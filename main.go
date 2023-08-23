package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Starting golang")
	count := 0

	go func() {
		for {
			select {
			case <-time.Tick(time.Second * 5):
				fmt.Println(count, " - Heartbeat")
				count = count + 1
			}
		}
	}()

	RunMqtt()
}
