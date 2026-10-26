FROM golang:1.24-alpine AS builder

WORKDIR /src

COPY app/main.go .

RUN CGO_ENABLED=0 GOOS=linux go build -o /server main.go

FROM alpine:3.22

WORKDIR /app

COPY --from=builder /server ./server

ENV APP_PORT=8000

EXPOSE 8000

USER 10001:10001

CMD ["/app/server"]
