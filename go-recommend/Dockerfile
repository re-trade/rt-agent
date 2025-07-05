FROM golang:1.23-alpine AS build

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o /product-recommendation main.go

FROM alpine:latest

WORKDIR /

COPY --from=build /product-recommendation /product-recommendation
EXPOSE 8080

CMD ["/movie-recommendation"]
