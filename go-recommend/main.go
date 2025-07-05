package main

import (
	"fmt"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
	"log"
	"net"
	"net/http"
	"recomgo/config"
	"recomgo/invoicer"
	qdrant2 "recomgo/qdrant"
	productServer "recomgo/server"
)

func main() {
	cfg := config.LoadConfig()
	log.Printf("Connecting to Qdrant at %s:6333", cfg.QdrantGrpcHost)
	if cfg.QdrantGrpcHost == "localhost" {
		alternativeHosts := []string{"host.docker.internal", "127.0.0.1", "qdrant"}

		log.Printf("Testing connection to Qdrant...")
		connected := false
		testURL := fmt.Sprintf("http://%s:6333/collections", cfg.QdrantGrpcHost)
		resp, err := http.Get(testURL)
		if err == nil {
			resp.Body.Close()
			connected = true
			log.Printf("Successfully connected to Qdrant at %s", testURL)
		} else {
			log.Printf("Cannot connect to Qdrant at %s: %v", testURL, err)
			for _, host := range alternativeHosts {
				if host == cfg.QdrantGrpcHost {
					continue
				}

				testURL = fmt.Sprintf("http://%s:6333/collections", host)
				log.Printf("Trying alternative Qdrant address: %s", testURL)

				resp, err := http.Get(testURL)
				if err == nil {
					resp.Body.Close()
					log.Printf("Successfully connected to Qdrant at %s", testURL)
					log.Printf("Consider updating your configuration to use %s instead of %s", host, cfg.QdrantGrpcHost)
					cfg.QdrantGrpcHost = host
					connected = true
					break
				}
			}
		}

		if !connected {
			log.Printf("\n======= QDRANT CONNECTION ERROR =======")
			log.Printf("Could not connect to Qdrant server. Please ensure that:")
			log.Printf("1. Qdrant is running")
			log.Printf("2. It's accessible at one of these addresses: localhost, 127.0.0.1, host.docker.internal, or qdrant")
			log.Printf("3. It's listening on port 6333")
			log.Printf("4. There are no firewall rules blocking the connection")
			log.Printf("5. If running in Docker, make sure the networks are properly configured")
			log.Printf("\nTo start Qdrant, you can run:")
			log.Printf("  docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
			log.Printf("\nThe server will continue running, but recommendation features may not work correctly.")
			log.Printf("=======================================\n")
		}
	}

	client, err := qdrant2.InitializeQdrant()
	if err != nil {
		log.Printf("Error initializing Qdrant client: %v", err)
		log.Printf("The server will continue running, but recommendation features may not work correctly.")
	} else {
		log.Printf("Qdrant client initialized successfully")
	}
	lis, err := net.Listen("tcp", ":8386")
	if err != nil {
		log.Fatalf("Cannot create listener: %v", err)
	}
	server := grpc.NewServer()
	service := productServer.NewServer(client, cfg.ProductConnectionName, cfg.QdrantGrpcHost)
	invoicer.RegisterRecommendationServiceServer(server, service)
	reflection.Register(server)

	log.Println("gRPC server is running on port 8386 with reflection API enabled")
	if err := server.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
