package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Starting golang")

	ticker := time.NewTicker(time.Second * 5)
	defer ticker.Stop()

	count := 0

	go func() {
		for range ticker.C {
			fmt.Println(count, " - Heartbeat")
			count = count + 1
		}
	}()

	RunMqtt()
}
