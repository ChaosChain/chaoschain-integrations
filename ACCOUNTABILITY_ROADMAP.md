# 🎯 Accountability Layer Roadmap

**Branch:** `feature/accountability-layer`  
**Goal:** Transform from "verifiable" to "accountable" - make proofs actionable and enforceable

---

## 📋 Current Status (What We Have)

✅ **Layer 1: AP2 Intent Verification** (Google)
- Intent mandates with JWT verification
- Cart mandates with payment authorization
- User consent and authorization flow

✅ **Layer 2: Process Integrity** (EigenCompute + 0G)
- Real TEE execution (Intel TDX)
- Deterministic AI outputs (EigenAI with temperature=0, seed=42)
- Execution hash matching (Alice vs Bob)
- Public proof endpoints
- 0G Storage for permanent proofs

✅ **Payments** (x402 + 0G)
- Direct A0GI transfers
- Payment receipts on-chain
- Protocol fee collection (2.5%)

---

## 🚀 Next Phase: Accountability Features

### **Priority 1: Real Enclave Signatures** 🔐 (HIGH IMPACT)

**Current State:**
```json
"signature": "TODO_ENCLAVE_SIGN_ee4fe1ab6d37605cf7b9ab9b7e09332b"
```

**Goal:** Sign proofs with TEE's private key

**Tasks:**
- [ ] Access EigenCompute enclave wallet private key
- [ ] Sign ProcessProof JSON with enclave key
- [ ] Verify signature matches enclave_wallet public key
- [ ] Update `/alice/proof` and `/bob/proof` endpoints

**Why it matters:** 
- Proves the proof came from the TEE (not spoofed)
- Enables third-party verification without trusting us
- Makes proofs cryptographically binding

**Files to modify:**
- `docker/genesis-agents/genesis_agents.py` (lines 388-448)
- Add signature verification to `agents/server_agent_sdk.py`

---

### **Priority 2: Link Payment ↔ Proof On-Chain** 💰 (PMF CRITICAL)

**Current State:**
- Payments happen (0.0008 A0GI)
- Proofs are stored (0G Storage)
- But they're **not linked**!

**Goal:** Embed proof CID in payment metadata/memo

**Tasks:**
- [ ] Add `proof_cid` field to x402 payment metadata
- [ ] Include execution_hash in payment memo
- [ ] Emit event linking payment TX → proof CID
- [ ] Update payment display to show proof link

**Why it matters:**
- Proves "we paid for THAT EXACT attested job"
- Enables dispute resolution (payment ↔ proof mismatch)
- Makes payments accountable (not just transfers)

**Files to modify:**
- `genesis_studio.py` (lines 863-1050, payment flow)
- `chaoschain_sdk` payment manager (add metadata support)

**Example:**
```python
payment_result = alice_sdk.x402_payment_manager.create_payment(
    to_address=alice_address,
    amount=0.001,
    metadata={
        "proof_cid": "0x71717241b1fe6594caedbca19238394c488d9f2eeb1e033b8a5e108cd24851c6",
        "exec_hash": "0x612352c554e09812e671a3f02af67f9a...",
        "service": "loan_evaluation",
        "app_id": "0xb29Ec00fF0D6C1349E6DFcD16234082aE60e64bb"
    }
)
```

---

### **Priority 3: Public Verification Page** 🌐 (DEMO IMPACT)

**Goal:** One-page explorer that shows the full accountability chain

**Tasks:**
- [ ] Create `/verify` endpoint in TEE app
- [ ] Display: Intent → TEE Proofs → Hash Match → Payment TX
- [ ] Add "Verify" button that runs local proof check
- [ ] Show all three layers in one view

**Why it matters:**
- Makes accountability visible (not just technical)
- Enables non-technical users to verify
- Perfect for demos and investor pitches

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 ChaosChain Accountability Explorer                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📋 Layer 1: Intent Verification                            │
│  ✅ AP2 Intent: "0.5 USDC micro-loan request"              │
│  ✅ JWT Verified: eyJhbGciOiJSUzI1NiIs...                   │
│                                                              │
│  🔐 Layer 2: Process Integrity                              │
│  ✅ Alice Proof: /alice/proof/8bd4c87f... [View]           │
│      Docker: sha256:4a368529...                             │
│      Exec Hash: 0x612352c5...                               │
│  ✅ Bob Proof: /bob/proof/64e65d6b... [View]               │
│      Docker: sha256:4a368529... ✅ MATCH                    │
│      Exec Hash: 0x612352c5... ✅ MATCH                      │
│                                                              │
│  💰 Layer 3: Payment Settlement                             │
│  ✅ Payment TX: 0xe7d6696c... [View on 0G]                 │
│      Amount: 0.0008 A0GI                                    │
│      Proof CID: 0x71717241... ✅ LINKED                     │
│                                                              │
│  📦 Storage: 0G Storage                                     │
│  ✅ Proof Stored: 0x71717241... [Download]                 │
│                                                              │
│  [🔍 Verify All] [📥 Download Proofs] [🔗 Share]          │
└─────────────────────────────────────────────────────────────┘
```

**Files to create:**
- `docker/genesis-agents/templates/verify.html`
- `docker/genesis-agents/genesis_agents.py` (add `/verify` route)

---

### **Priority 4: Deterministic Re-run Demo** 🔄 (EIGENLAYER VALIDATION)

**Goal:** One-command demo that proves determinism

**Current State:**
- Alice runs → hash A
- Bob re-runs → hash B
- They match ✅
- But it's buried in logs

**Goal:** Make it a standalone, shareable demo

**Tasks:**
- [ ] Create `demo_determinism.py` script
- [ ] Run Alice's evaluation
- [ ] Run Bob's re-execution
- [ ] Compare hashes with visual diff
- [ ] Auto-release payment if match
- [ ] Generate shareable report

**Why it matters:**
- Proves EigenLayer's determinism claim
- Makes it easy for others to reproduce
- Perfect for technical audiences

**Example output:**
```
🔬 DETERMINISTIC VERIFICATION DEMO
═══════════════════════════════════════════════════════════

Step 1: Alice evaluates loan in TEE...
✅ Decision: REJECT
✅ Risk Score: 85/100
✅ Exec Hash: 0x612352c554e09812e671a3f02af67f9a...

Step 2: Bob re-executes with SAME inputs...
✅ Decision: REJECT
✅ Risk Score: 85/100
✅ Exec Hash: 0x612352c554e09812e671a3f02af67f9a...

Step 3: Compare hashes...
Alice: 0x612352c554e09812e671a3f02af67f9a...
Bob:   0x612352c554e09812e671a3f02af67f9a...
       ✅ IDENTICAL MATCH

Step 4: Auto-release payment...
✅ Payment released: 0.001 A0GI (Charlie → Alice)
✅ TX: 0xe7d6696c...

🎉 DETERMINISM PROVEN
Same inputs → Same outputs → Same hash → Automatic settlement
```

**Files to create:**
- `demos/deterministic_verification.py`
- `demos/README.md`

---

### **Priority 5: Enhanced Evidence Packages** 📦 (COMPLETENESS)

**Goal:** Make evidence packages self-contained and verifiable

**Tasks:**
- [ ] Include all three layer proofs in one package
- [ ] Add verification instructions
- [ ] Include signature verification code
- [ ] Add merkle proofs from 0G Storage
- [ ] Generate PDF report

**Why it matters:**
- Makes proofs portable (download once, verify anywhere)
- Enables offline verification
- Professional presentation for audits

**Package structure:**
```json
{
  "evidence_id": "loan_eval_2025_10_21_...",
  "timestamp": "2025-10-21T11:08:09Z",
  "layers": {
    "layer1_intent": {
      "ap2_mandate": {...},
      "jwt_token": "...",
      "verification_status": "verified"
    },
    "layer2_integrity": {
      "alice_proof": {...},
      "bob_proof": {...},
      "hash_match": true,
      "signatures_verified": true
    },
    "layer3_payment": {
      "payment_tx": "0xe7d6696c...",
      "amount": "0.0008 A0GI",
      "proof_cid": "0x71717241...",
      "link_verified": true
    }
  },
  "storage": {
    "0g_uri": "0g://object/71717241...",
    "0g_tx": "0x153c6273...",
    "merkle_proof": [...]
  },
  "verification": {
    "instructions": "...",
    "verification_script": "verify.py",
    "expected_hashes": {...}
  }
}
```

---

### **Priority 6: Separate TEE Deployments** 🏢 (TRUST MINIMIZATION)

**Current State:**
- Alice + Bob in SAME TEE app
- Same enclave wallet
- Reduces trust assumptions slightly

**Goal:** Deploy Alice and Bob to separate TEEs

**Tasks:**
- [ ] Create separate Dockerfiles for Alice and Bob
- [ ] Deploy to different EigenCompute apps
- [ ] Update genesis_studio.py to use different app_ids
- [ ] Verify different enclave wallets

**Why it matters:**
- Stronger trust model (no collusion possible)
- Better demonstrates TEE isolation
- More realistic production setup

**Files to create:**
- `docker/alice-agent/Dockerfile`
- `docker/bob-agent/Dockerfile`
- Update deployment scripts

---

## 📊 Success Metrics

### **Technical Metrics:**
- [ ] All proofs cryptographically signed
- [ ] 100% payment ↔ proof linkage
- [ ] < 5 second verification time
- [ ] Zero mock/placeholder code

### **Demo Metrics:**
- [ ] One-click verification page works
- [ ] Determinism demo runs in < 60 seconds
- [ ] Evidence packages downloadable and verifiable
- [ ] All three layers visible in explorer

### **Business Metrics:**
- [ ] Can pitch as "accountable AI" (not just "verifiable")
- [ ] Third parties can verify without our help
- [ ] Ready for institutional customers
- [ ] Clear path to $100M valuation

---

## 🎯 Recommended Order

**Week 1: Foundation**
1. Real enclave signatures (Priority 1)
2. Link payment ↔ proof (Priority 2)

**Week 2: Visibility**
3. Public verification page (Priority 3)
4. Deterministic re-run demo (Priority 4)

**Week 3: Polish**
5. Enhanced evidence packages (Priority 5)
6. Separate TEE deployments (Priority 6)

---

## 🔥 Quick Wins (Can Do Today)

1. **Add proof_cid to payment display** (30 min)
   - Update `genesis_studio.py` payment summary
   - Show the link between payment TX and proof CID

2. **Create verification instructions** (1 hour)
   - Document how to verify proofs
   - Add to README.md

3. **Improve proof endpoint response** (30 min)
   - Add more metadata to `/alice/proof` response
   - Include verification instructions in JSON

---

## 💡 Next Steps

1. **Pick Priority 1 or 2** to start with
2. **Create task breakdown** for chosen priority
3. **Start implementation**

Which priority should we tackle first? 🚀

