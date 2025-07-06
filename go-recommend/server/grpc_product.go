package server

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"sort"

	"github.com/qdrant/go-client/qdrant"
	"recomgo/invoicer"
)

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

func (s *Server) GetVectorById(ctx context.Context, pointId string) ([]float32, error) {
	getResp, err := s.qdrantClient.GetPointsClient().Get(ctx, &qdrant.GetPoints{
		CollectionName: s.Collection,
		Ids: []*qdrant.PointId{
			{PointIdOptions: &qdrant.PointId_Uuid{Uuid: pointId}},
		},
		WithVectors: &qdrant.WithVectorsSelector{
			SelectorOptions: &qdrant.WithVectorsSelector_Enable{Enable: true},
		},
	})
	if err != nil {
		log.Printf("Error retrieving vector for %s: %v", pointId, err)
		return nil, err
	}
	if len(getResp.Result) == 0 {
		return nil, nil
	}
	vector := getResp.Result[0].Vectors.GetVector().Data
	return vector, nil
}

func (s *Server) RecommendByProductId(ctx context.Context, in *invoicer.ProductRequest) (*invoicer.ProductResponse, error) {
	pointID := in.GetProductId()
	if pointID == "" {
		return errorResponse("INVALID_INPUT", "Empty ID provided.")
	}

	vector, err := s.GetVectorById(ctx, pointID)
	if err != nil || len(vector) == 0 {
		return errorResponse("NO_VECTOR_DATA", fmt.Sprintf("No vector for ID %s", pointID))
	}

	pageSize, page := getPageParams(in)
	offset := (page - 1) * pageSize

	resp, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
		CollectionName: s.Collection,
		Query:          qdrant.NewQuery(vector...),
		Limit:          qdrant.PtrOf(uint64(pageSize)),
		Offset:         qdrant.PtrOf(uint64(offset)),
		WithPayload:    qdrant.NewWithPayloadInclude("name"),
	})
	if err != nil {
		log.Printf("Qdrant query error: %v", err)
		return errorResponse("QUERY_ERROR", "Search failed.")
	}

	var items []*invoicer.ScoreItem
	for _, r := range resp {
		items = append(items, &invoicer.ScoreItem{
			Id:    r.Id.GetUuid(),
			Score: r.Score,
		})
	}

	return &invoicer.ProductResponse{
		Items:      items,
		TotalPages: 1, // Qdrant doesn’t return total count unless you prefetch all.
	}, nil
}

func (s *Server) ListSimilar(ctx context.Context, in *invoicer.ProductRequest) (*invoicer.ProductResponse, error) {
	historyIDs := in.GetProductIds()
	if len(historyIDs) == 0 {
		return errorResponse("INVALID_INPUT", "No IDs provided.")
	}

	scoreMap := make(map[string]float32)

	for _, id := range historyIDs {
		vector, err := s.GetVectorById(ctx, id)
		if err != nil || len(vector) == 0 {
			log.Printf("Skipping ID %s: %v", id, err)
			continue
		}

		results, err := s.qdrantClient.Query(ctx, &qdrant.QueryPoints{
			CollectionName: s.Collection,
			Query:          qdrant.NewQuery(vector...),
			WithPayload:    qdrant.NewWithPayloadInclude("name"),
			Limit:          qdrant.PtrOf(uint64(100)), // optional cap
		})
		if err != nil {
			log.Printf("Query failed for ID %s: %v", id, err)
			continue
		}

		for _, hit := range results {
			uuid := hit.Id.GetUuid()
			if uuid == id {
				continue
			}
			if scoreMap[uuid] < hit.Score {
				scoreMap[uuid] = hit.Score
			}
		}
	}

	if len(scoreMap) == 0 {
		return errorResponse("NO_SIMILAR_FOUND", "No similar items found.")
	}

	var max float32
	for _, v := range scoreMap {
		if v > max {
			max = v
		}
	}

	var scored []*invoicer.ScoreItem
	for id, score := range scoreMap {
		scored = append(scored, &invoicer.ScoreItem{
			Id:    id,
			Score: score / max,
		})
	}

	sort.Slice(scored, func(i, j int) bool {
		return scored[i].Score > scored[j].Score
	})

	pageSize, page := getPageParams(in)
	offset := (page - 1) * pageSize
	end := offset + pageSize
	if offset > len(scored) {
		offset = len(scored)
	}
	if end > len(scored) {
		end = len(scored)
	}

	totalPages := (len(scored) + pageSize - 1) / pageSize
	return &invoicer.ProductResponse{
		Items:      scored[offset:end],
		TotalPages: int32(totalPages),
	}, nil
}

func getPageParams(in *invoicer.ProductRequest) (int, int) {
	pageSize := int(in.GetPageSize())
	if pageSize <= 0 {
		pageSize = 10
	}
	page := int(in.GetPage())
	if page <= 0 {
		page = 1
	}
	return pageSize, page
}

func errorResponse(code, msg string) (*invoicer.ProductResponse, error) {
	return &invoicer.ProductResponse{
		Error: &invoicer.ErrorResponse{
			ErrorCode:    code,
			ErrorMessage: msg,
		},
	}, nil
}
