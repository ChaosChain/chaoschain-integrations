.PHONY: help proto build test clean run

BINARY_STORAGE=bin/zerog-storage-bridge
BINARY_COMPUTE=bin/zerog-compute-bridge
PROTO_DIR=../proto
PKG_DIR=pkg

help:
	@echo "ZeroG Sidecar Build Commands"
	@echo "============================="
	@echo "  make proto         - Generate gRPC code from proto files"
	@echo "  make build         - Build all binaries"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make run-storage   - Run storage bridge"
	@echo "  make run-compute   - Run compute bridge"

proto:
	@echo "Generating gRPC code..."
	mkdir -p $(PKG_DIR)/storage $(PKG_DIR)/compute
	protoc --go_out=$(PKG_DIR)/storage --go_opt=paths=source_relative \
		--go-grpc_out=$(PKG_DIR)/storage --go-grpc_opt=paths=source_relative \
		-I $(PROTO_DIR) $(PROTO_DIR)/zerog_storage.proto
	protoc --go_out=$(PKG_DIR)/compute --go_opt=paths=source_relative \
		--go-grpc_out=$(PKG_DIR)/compute --go-grpc_opt=paths=source_relative \
		-I $(PROTO_DIR) $(PROTO_DIR)/zerog_compute.proto
	@echo "Done!"

build: proto
	@echo "Building ZeroG sidecars..."
	mkdir -p bin
	go build -o $(BINARY_STORAGE) cmd/storage-bridge/main.go
	go build -o $(BINARY_COMPUTE) cmd/compute-bridge/main.go
	@echo "Binaries built: $(BINARY_STORAGE), $(BINARY_COMPUTE)"

test:
	go test -v ./...

clean:
	rm -rf bin/
	rm -rf $(PKG_DIR)/storage/*.pb.go
	rm -rf $(PKG_DIR)/compute/*.pb.go

run-storage: build
	$(BINARY_STORAGE) --port 50051

run-compute: build
	$(BINARY_COMPUTE) --port 50052

