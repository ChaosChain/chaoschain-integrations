# 🔌 ChaosChain Provider Templates

This directory contains **template files** to help you quickly create your own provider integration for ChaosChain.

---

## 📋 **Available Templates**

### **1. Compute Provider Template**
- **File**: `compute_provider_template.py`
- **Use For**: LLM inference, ML training, verifiable compute
- **Examples**: Gaia, Akash, Ritual, Morpheus, Bittensor

### **2. Storage Provider Template**
- **File**: `storage_provider_template.py`
- **Use For**: Decentralized data storage, agent memory, audit logs
- **Examples**: Arweave, Filecoin, Storj, Greenfield, Walrus

### **3. TEE Provider Template**
- **File**: `tee_provider_template.py` (coming soon)
- **Use For**: Hardware-verified identity, secure key management
- **Examples**: Phala, Oasis, Secret Network, Intel SGX

---

## 🚀 **Quick Start**

### **Step 1: Copy Template**

```bash
# For compute provider
cp compute_provider_template.py my_provider_compute.py

# For storage provider
cp storage_provider_template.py my_provider_storage.py
```

### **Step 2: Replace Placeholders**

Search and replace in your file:
- `YourProvider` → Your provider name (e.g., `Gaia`, `Arweave`)
- `yourprovider` → Your provider name in lowercase (e.g., `gaia`, `arweave`)
- `https://api.yourprovider.com` → Your actual API endpoint

### **Step 3: Implement TODOs**

Each template has `TODO` comments marking what you need to implement:
- `submit()` / `put()` - Submit tasks or store data
- `status()` / `get()` - Check status or retrieve data
- `result()` / `verify()` - Get results or verify integrity

### **Step 4: Test Locally**

```python
# test_my_provider.py

from chaoschain_sdk import ChaosChainSDK
import my_provider_compute  # Auto-registers

sdk = ChaosChainSDK(
    compute_provider="myprovider",
    compute_config={"api_key": "test-key"}
)

# Test it!
result = sdk.compute.submit({
    "model": "llama-3-8b",
    "prompt": "Hello, world!"
})

print(result)
```

### **Step 5: Publish**

```bash
# Create package structure
mkdir chaoschain-provider-myprovider
cd chaoschain-provider-myprovider

# Add your provider file
cp ../my_provider_compute.py ./

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="chaoschain-provider-myprovider",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "chaoschain-sdk>=0.1.0",
    ],
    author="Your Name",
    description="MyProvider integration for ChaosChain",
    url="https://github.com/yourorg/chaoschain-provider-myprovider",
)
EOF

# Publish to PyPI
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

## 📚 **Full Documentation**

See the complete integration guide: [PROVIDER_INTEGRATION_GUIDE.md](../../../PROVIDER_INTEGRATION_GUIDE.md)

---

## 🤝 **Get Help**

- **Discord**: [Join ChaosChain Discord](https://discord.gg/chaoschain)
- **GitHub**: [chaoschain-integrations](https://github.com/chaoschain/chaoschain-integrations)
- **Email**: integrations@chaoschain.ai

---

**Happy building!** 🚀

