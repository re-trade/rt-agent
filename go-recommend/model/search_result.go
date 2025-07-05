package model

type SearchResult struct {
	ID      string `json:"id"`
	Score   string `json:"score"`
	Payload any    `json:"payload"`
}
