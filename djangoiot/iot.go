package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Starting golang")
	count := 0
	for {
		select {
		case <-time.Tick(time.Second * 5):
			fmt.Println(count, " - Timeout")
			count = count+1
		}
	}
}
