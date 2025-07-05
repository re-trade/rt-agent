package handler

import (
	"log"
	"net/http"
	"recomgo/service"

	"github.com/gin-gonic/gin"
	"github.com/qdrant/go-client/qdrant"
)

func SearchHandler(client *qdrant.Client) gin.HandlerFunc {
	return func(c *gin.Context) {

		var queryVector []float64
		if err := c.ShouldBindJSON(&queryVector); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
			return
		}

		log.Println(queryVector)
		results, err := service.SearchProducts(client, queryVector)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error executing search"})
			return
		}

		c.JSON(http.StatusOK, results)
	}
}
