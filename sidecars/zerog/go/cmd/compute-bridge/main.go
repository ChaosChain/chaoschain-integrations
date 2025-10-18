package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

var (
	port    = flag.Int("port", 50052, "The gRPC server port")
	version = "0.1.0"
)

func main() {
	flag.Parse()

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()

	// TODO: Register ZeroG compute service implementation
	// pb.RegisterZeroGComputeServer(s, &server{})

	// Register reflection service (for grpcurl, etc.)
	reflection.Register(s)

	log.Printf("ZeroG Compute Bridge v%s listening on port %d", version, *port)
	log.Println("TODO: Implement actual ZeroG SDK integration")

	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
