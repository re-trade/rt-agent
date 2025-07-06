package qdrant

import (
	"context"
	"fmt"
	"github.com/qdrant/go-client/qdrant"
	"recomgo/config"
)

func getProductCollectionName() string {
	cfg := config.LoadConfig()
	return cfg.ProductConnectionName
}

func getVectorsize() uint64 {
	cfg := config.LoadConfig()
	return cfg.VectorSize
}

func InitializeQdrant() (*qdrant.Client, error) {
	cfg := config.LoadConfig()
	client, err := qdrant.NewClient(&qdrant.Config{
		Host: cfg.QdrantGrpcHost,
		Port: cfg.QdrantGrpcPort,
	})
	if err != nil {
		return nil, fmt.Errorf("failed To Connected To Qdrant: %v", err)
	}
	fmt.Println("Qdrant Connected !!!")
	collectionName := getProductCollectionName()
	resp, err := client.ListCollections(context.Background())
	if err != nil {
		return nil, err
	}
	for _, name := range resp {
		if name == collectionName {
			fmt.Println("Qdrant Collection Already Exists !!!")
			return client, nil
		}
	}
	err = client.CreateCollection(context.Background(), &qdrant.CreateCollection{
		CollectionName: getProductCollectionName(),
		VectorsConfig: qdrant.NewVectorsConfig(&qdrant.VectorParams{
			Size:     getVectorsize(),
			Distance: qdrant.Distance_Cosine,
		}),
	})
	if err != nil {
		return nil, err
	}
	fmt.Println("Qdrant Created Collection !!!")

	return client, nil
}
