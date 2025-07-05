package service

import (
	"context"
	"github.com/qdrant/go-client/qdrant"
	"recomgo/config"
	"recomgo/helpers"
	"recomgo/model"
	"strconv"
)

func ProductCollectionName() string {
	cfg := config.LoadConfig()
	return cfg.ProductConnectionName
}

func SearchProducts(client *qdrant.Client, queryVector []float64) ([]model.SearchResult, error) {
	vector32 := helpers.ConvertToFloat32(queryVector)

	queryResult, err := client.Query(context.Background(), &qdrant.QueryPoints{
		CollectionName: ProductCollectionName(),
		Query:          qdrant.NewQuery(vector32...),
		WithPayload:    qdrant.NewWithPayloadInclude("name"),
	})

	if err != nil {
		return nil, err
	}
	var results []model.SearchResult
	for _, hit := range queryResult {
		scoreAsString := strconv.FormatFloat(float64(hit.Score), 'f', -1, 64)
		results = append(results, model.SearchResult{
			ID:      hit.Id.GetUuid(),
			Score:   scoreAsString,
			Payload: hit.Payload["name"],
		})
	}

	return results, nil
}
