FROM lukemathwalker/cargo-chef:latest-rust-1 AS chef
WORKDIR /app

FROM chef AS planner
COPY Cargo.toml Cargo.lock ./
COPY src/ ./src
RUN apt-get update \
    && apt-get install protobuf-compiler -y
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder 
COPY --from=planner /app/recipe.json recipe.json

RUN apt-get update \
    && apt-get install protobuf-compiler -y
RUN cargo chef cook --release --recipe-path recipe.json
COPY . .
RUN cargo build --release

FROM debian:bookworm AS application

RUN apt-get update \
    && apt-get install libssl3 ca-certificates -y \
    && apt-get clean

WORKDIR /app

COPY --from=builder /app/target/release/id-card-extractor .

CMD ["./id-card-extractor"]
