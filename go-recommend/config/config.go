package config

import (
	"os"
	"strconv"
	"strings"
)

type Config struct {
	ProductConnectionName string
	VectorSize            uint64
	DevMode               bool
	QdrantHttpPort        int
	QdrantGrpcPort        int
	QdrantGrpcHost        string
	QdrantHttpHost        string
	QdrantAltHosts        []string
}

func LoadConfig() Config {
	devModeStr := os.Getenv("DEV")
	devMode, err := strconv.ParseBool(devModeStr)
	if err != nil {
		devMode = false
	}

	qdrantHTTPPortStr := os.Getenv("QDRANT_HTTP")
	qdrantHTTPPort, err := strconv.Atoi(qdrantHTTPPortStr)
	if err != nil {
		qdrantHTTPPort = 6333
	}

	qdrantGRPCPortStr := os.Getenv("QDRANT_GRPC")
	qdrantGRPCPort, err := strconv.Atoi(qdrantGRPCPortStr)
	if err != nil {
		qdrantGRPCPort = 6334
	}

	qdrantHost := os.Getenv("QDRANT_HOST")
	if qdrantHost == "" {
		qdrantHost = "localhost"
	}

	qdrantHTTPHost := os.Getenv("QDRANT_HTTP_HOST")
	if qdrantHTTPHost == "" {
		qdrantHTTPHost = qdrantHost
	}

	altHostsEnv := os.Getenv("QDRANT_ALT_HOSTS")
	var altHosts []string
	if altHostsEnv != "" {
		altHosts = strings.Split(altHostsEnv, ",")
	} else {
		altHosts = []string{"qdrantdb", "qdrant", "vectordb"}
	}

	productCollectionName := os.Getenv("QDRANT_PRODUCT_COLLECTION_NAME")
	if productCollectionName == "" {
		productCollectionName = "product"
	}

	vectorSizeStr := os.Getenv("VECTOR_SIZE")
	vectorSize, err := strconv.Atoi(vectorSizeStr)
	if err != nil || vectorSize <= 0 {
		vectorSize = 50
	}

	return Config{
		DevMode:               devMode,
		QdrantHttpPort:        qdrantHTTPPort,
		QdrantGrpcPort:        qdrantGRPCPort,
		QdrantGrpcHost:        qdrantHost,
		QdrantHttpHost:        qdrantHTTPHost,
		ProductConnectionName: productCollectionName,
		VectorSize:            uint64(vectorSize),
		QdrantAltHosts:        altHosts,
	}
}
