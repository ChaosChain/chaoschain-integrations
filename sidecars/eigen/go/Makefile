.PHONY: help proto build test clean run

BINARY=bin/eigen-compute-bridge
PROTO_DIR=../proto
PKG_DIR=pkg

help:
	@echo "Eigen Sidecar Build Commands"
	@echo "============================"
	@echo "  make proto    - Generate gRPC code from proto files"
	@echo "  make build    - Build binary"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make run      - Run compute bridge"

proto:
	@echo "Generating gRPC code..."
	mkdir -p $(PKG_DIR)/compute
	protoc --go_out=$(PKG_DIR)/compute --go_opt=paths=source_relative \
		--go-grpc_out=$(PKG_DIR)/compute --go-grpc_opt=paths=source_relative \
		-I $(PROTO_DIR) $(PROTO_DIR)/eigen_compute.proto
	@echo "Done!"

build: proto
	@echo "Building Eigen sidecar..."
	mkdir -p bin
	go build -o $(BINARY) cmd/compute-bridge/main.go
	@echo "Binary built: $(BINARY)"

test:
	go test -v ./...

clean:
	rm -rf bin/
	rm -rf $(PKG_DIR)/compute/*.pb.go

run: build
	$(BINARY) --port 50053

