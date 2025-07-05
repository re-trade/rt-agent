package server

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/qdrant/go-client/qdrant"
	"io"
	"log"
	"net/http"
	"recomgo/helpers"
	"recomgo/invoicer"
	"sort"
	"strings"
)

type QdrantPointResponse struct {
	Result struct {
		ID      int                    `json:"id"`
		Payload map[string]interface{} `json:"payload"`
		Vector  []float64              `json:"vector"`
	} `json:"result"`
	Status interface{} `json:"status"`
	Time   float64     `json:"time"`
}

type Server struct {
	qdrantClient *qdrant.Client
	Collection   string
	invoicer.RecommendationServiceServer
	httpClient *http.Client
	qdrantHost string
}

func NewServer(client *qdrant.Client, collection string, qdrantHost string) *Server {
	return &Server{
		qdrantClient: client,
		Collection:   collection,
		httpClient:   &http.Client{},
		qdrantHost:   qdrantHost,
	}
}

func (s *Server) RecommendByProductId(ctx context.Context, in *invoicer.ProductRequest) (*invoicer.ProductResponse, error) {
	pointID := in.ProductId
	log.Printf("Received Create request with UUID: %s", pointID)

	if pointID == "" {
		log.Printf("Empty ID provided in request")
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "INVALID_INPUT",
				ErrorMessage: "Empty ID provided. Please provide a valid ID.",
			},
		}, nil
	}

	url := fmt.Sprintf("http://%s:6333/collections/%s/points/%s", s.qdrantHost, s.Collection, pointID)
	log.Printf("Retrieving point from Qdrant at URL: %s", url)

	resp, err := http.Get(url)
	if err != nil {
		log.Printf("Error retrieving point from Qdrant: %v", err)
		var errorMessage string
		if strings.Contains(err.Error(), "connection refused") {
			errorMessage = fmt.Sprintf("Cannot connect to Qdrant server at %s:6333. Make sure the server is running and accessible.", s.qdrantHost)
		} else {
			errorMessage = fmt.Sprintf("Failed to retrieve point with UUID %s from Qdrant: %v", pointID, err)
		}

		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "RETRIEVE_ERROR",
				ErrorMessage: errorMessage,
			},
		}, nil
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Printf("Error closing response body from Qdrant: %v", err)
		}
	}(resp.Body)

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Error reading response body from Qdrant: %v", err)
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "READ_ERROR",
				ErrorMessage: fmt.Sprintf("Failed to read response from Qdrant for UUID %s", pointID),
			},
		}, nil
	}

	log.Printf("Raw Response Body: %s", string(body))

	// Unmarshal the JSON response
	var pointResponse QdrantPointResponse
	err = json.Unmarshal(body, &pointResponse)
	if err != nil {
		log.Printf("Error unmarshalling response from Qdrant: %v", err)
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "PARSE_ERROR",
				ErrorMessage: fmt.Sprintf("Unexpected response format received from Qdrant for UUID %s", pointID),
			},
		}, nil
	}

	switch status := pointResponse.Status.(type) {
	case string:
		if status != "ok" {
			log.Printf("Unexpected status from Qdrant: %s", status)
			return &invoicer.ProductResponse{
				Error: &invoicer.ErrorResponse{
					ErrorCode:    "STATUS_ERROR",
					ErrorMessage: fmt.Sprintf("Unexpected status received from Qdrant: %s", status),
				},
			}, nil
		}
	case map[string]interface{}:
		if errMsg, ok := status["error"].(string); ok {
			log.Printf("Error response from Qdrant: %s", errMsg)
			return &invoicer.ProductResponse{
				Error: &invoicer.ErrorResponse{
					ErrorCode:    "NOT_FOUND",
					ErrorMessage: fmt.Sprintf("Qdrant error: %s", errMsg),
				},
			}, nil
		}
	default:
		log.Printf("Unknown status type in response from Qdrant")
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "UNKNOWN_STATUS",
				ErrorMessage: fmt.Sprintf("Unknown status type in response from Qdrant for UUID %s", pointID),
			},
		}, nil
	}

	point := pointResponse.Result.Vector
	if len(point) == 0 {
		log.Printf("No vector data found for UUID: %s", pointID)
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "NO_VECTOR_DATA",
				ErrorMessage: fmt.Sprintf("No vector data found for UUID: %s", pointID),
			},
		}, nil
	}
	log.Printf("Retrieved point vector: %+v", point)

	countQueryResult, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
		CollectionName: s.Collection,
		Query:          qdrant.NewQuery(helpers.ConvertToFloat32(point)...),
		Limit:          qdrant.PtrOf(uint64(1000)),
	})
	if err != nil {
		log.Printf("Error querying Qdrant for total similar items: %v", err)
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "QUERY_ERROR",
				ErrorMessage: fmt.Sprintf("Failed to query Qdrant for total similar items for UUID %s", pointID),
			},
		}, nil
	}

	totalResults := len(countQueryResult)
	totalPages := (totalResults + int(in.GetPageSize()) - 1) / int(in.GetPageSize())

	pageSize := in.GetPageSize()
	page := in.GetPage()
	offset := (page - 1) * pageSize

	queryResult, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
		CollectionName: s.Collection,
		Query:          qdrant.NewQuery(helpers.ConvertToFloat32(point)...),
		WithPayload:    qdrant.NewWithPayloadInclude("name"),
		Limit:          qdrant.PtrOf(uint64(pageSize)),
		Offset:         qdrant.PtrOf(uint64(offset)),
	})
	if err != nil {
		log.Printf("Error querying Qdrant for similar items: %v", err)
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "QUERY_ERROR",
				ErrorMessage: fmt.Sprintf("Failed to query Qdrant for similar items for UUID %s", pointID),
			},
		}, nil
	}

	if queryResult == nil {
		log.Printf("No similar items found for point with UUID: %s", pointID)
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "NO_SIMILAR_ITEMS",
				ErrorMessage: fmt.Sprintf("No similar items found for UUID %s", pointID),
			},
		}, nil
	}

	var scoredItems []*invoicer.ScoreItem
	for _, hit := range queryResult {
		score := hit.Score
		log.Printf("Processing hit with UUID: %s and Score: %f", hit.Id.GetUuid(), score)

		scoredItems = append(scoredItems, &invoicer.ScoreItem{
			Id:    strings.Split(hit.GetId().String(), ":")[1],
			Score: score,
		})
	}

	log.Printf("Returning CreateResponse with scored items: %+v", scoredItems)

	return &invoicer.ProductResponse{
		Items:      scoredItems,
		TotalPages: int32(totalPages),
	}, nil
}

func (s *Server) ListSimilar(ctx context.Context, in *invoicer.ProductRequest) (*invoicer.ProductResponse, error) {
	historyIDs := in.ProductIds
	pageSize := in.GetPageSize()
	page := in.GetPage()
	offset := (page - 1) * pageSize

	log.Printf("Received Create request with history IDs: %v", historyIDs)

	if len(historyIDs) == 0 {
		log.Printf("No IDs provided in request")
		return &invoicer.ProductResponse{
			Error: &invoicer.ErrorResponse{
				ErrorCode:    "INVALID_INPUT",
				ErrorMessage: "No IDs provided. Please provide at least one valid ID.",
			},
		}, nil
	}

	scoreMap := make(map[string]float64)
	payloadMap := make(map[string]string)

	for _, id := range historyIDs {
		url := fmt.Sprintf("http://%s:6333/collections/%s/points/%s", s.qdrantHost, s.Collection, id)
		resp, err := http.Get(url)
		if err != nil {
			log.Printf("Error retrieving point for ID %s: %v", id, err)
			continue
		}
		defer resp.Body.Close()

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			log.Printf("Error reading response body for ID %s: %v", id, err)
			continue
		}

		var pointResponse QdrantPointResponse
		err = json.Unmarshal(body, &pointResponse)
		if err != nil {
			log.Printf("Error unmarshalling response for ID %s: %v", id, err)
			continue
		}

		point := pointResponse.Result.Vector
		if len(point) == 0 {
			log.Printf("No vector data found for ID: %s", id)
			continue
		}
		log.Printf("Vector for ID %s: %v", id, point)

		queryResult, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
			CollectionName: s.Collection,
			Query:          qdrant.NewQuery(helpers.ConvertToFloat32(point)...),
			WithPayload:    qdrant.NewWithPayloadInclude("name"),
			Limit:          qdrant.PtrOf(uint64(1000)),
		})
		if err != nil {
			log.Printf("Error querying similar items for ID %s: %v", id, err)
			continue
		}

		for _, hit := range queryResult {
			uuid := strings.Split(hit.GetId().String(), ":")[1]
			title := hit.Payload["name"].GetStringValue()
			score := hit.Score
			log.Printf("ID: %s, Name: %s, Score: %f", uuid, title, score)
			if _, seen := scoreMap[uuid]; seen {
				scoreMap[uuid] = float64(score)
			} else {
				scoreMap[uuid] = float64(score)
				payloadMap[uuid] = title
			}
		}
	}

	for _, id := range historyIDs {
		delete(scoreMap, string(id))
	}

	var maxScore float64
	for _, score := range scoreMap {
		if score > maxScore {
			maxScore = score
		}
	}

	if maxScore > 0 {
		for uuid := range scoreMap {
			scoreMap[uuid] = scoreMap[uuid] / maxScore
		}
	}

	var scoredItems []*invoicer.ScoreItem
	for uuid, score := range scoreMap {
		scoredItems = append(scoredItems, &invoicer.ScoreItem{
			Id:    uuid,
			Score: float32(score),
		})
	}

	sort.Slice(scoredItems, func(i, j int) bool {
		return scoredItems[i].Score > scoredItems[j].Score
	})

	totalResults := len(scoredItems)
	totalPages := (totalResults + int(pageSize) - 1) / int(pageSize)

	start := offset
	end := offset + int32(pageSize)
	if int(start) > totalResults {
		start = int32(totalResults)
	}
	if end > int32(totalResults) {
		end = int32(totalResults)
	}
	paginatedItems := scoredItems[start:end]

	return &invoicer.ProductResponse{
		Items:      paginatedItems,
		TotalPages: int32(totalPages),
	}, nil
}
