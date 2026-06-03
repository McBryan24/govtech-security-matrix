import time
import json

class ZeroTrustGateway:
    """
    Implements Module 3 Technical Audit Criteria: API Interoperability & Zero-Trust.
    Enforces tokenized, boolean query responses to prevent lateral database scraping
    during inter-agency data sharing.
    """
    def __init__(self):
        # Simulated central registry of verified biometric hashes.
        # In a production environment, this is the highly secured NITA-U national database.
        self.central_registry = {
            "GOVNET_REQ_9942": "4f28774b96e71a5646bcb6eebbe492c69ae4fbe8117bbfb192ee07a214e70b5a"
        }
        # Memory block for the automated rate limiter
        self.request_logs = {}

    def enforce_rate_limit(self, agency_id: str) -> bool:
        """Simulates a strict rate limiter to prevent automated API scraping."""
        current_time = time.time()
        if agency_id in self.request_logs:
            last_request = self.request_logs[agency_id]
            if current_time - last_request < 1.0: # Strict limit: Max 1 request per second
                return False
        self.request_logs[agency_id] = current_time
        return True

    def process_verification_request(self, agency_id: str, request_id: str, submitted_hash: str):
        """
        Processes the inter-agency request using strict Data Minimization.
        NEVER returns PII. Returns ONLY a cryptographic boolean token.
        """
        print(f"[*] Gateway routing verification request from {agency_id}...")
        
        # 1. Audit Check: Rate Limit Enforced
        if not self.enforce_rate_limit(agency_id):
            return {
                "status": "429 Too Many Requests", 
                "verification_token": None, 
                "audit_flag": "Rate limit exceeded. Potential lateral scraping detected."
            }

        # 2. Audit Check: Verify Identity via Hash Matching (Zero-Knowledge)
        is_verified = False
        if request_id in self.central_registry:
            if self.central_registry[request_id] == submitted_hash:
                is_verified = True

        # 3. Construct Tokenized Response (The core of the Zero-Trust mandate)
        response_token = {
            "status": "200 OK",
            "agency_id": agency_id,
            "request_id": request_id,
            "identity_verified": is_verified, # Boolean only! No demographic payload.
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        return response_token

# --- EXECUTE SIMULATION ---
if __name__ == "__main__":
    print("="*65)
    print(" INITIALIZING GOVTECH MODULE 3: ZERO-TRUST API GATEWAY ")
    print("="*65)
    
    gateway = ZeroTrustGateway()
    
    # Scenario: Ministry of Health Clinic is attempting to verify a patient's digital ID.
    # The clinic scans the fingerprint locally and submits ONLY the hash, not the image.
    agency = "MoH_Clinic_Terminal_04"
    patient_id = "GOVNET_REQ_9942"
    clinic_submitted_hash = "4f28774b96e71a5646bcb6eebbe492c69ae4fbe8117bbfb192ee07a214e70b5a"
    
    print("\n[!] SCENARIO 1: Legitimate Inter-Agency Verification")
    response = gateway.process_verification_request(agency, patient_id, clinic_submitted_hash)
    print(json.dumps(response, indent=4))
    
    print("\n[!] SCENARIO 2: Malicious Lateral Scraping Attempt (Rate Limit Trigger)")
    print("[*] Simulating compromised peripheral endpoint rapidly querying the registry...")
    response = gateway.process_verification_request(agency, "GOVNET_REQ_9943", "dummyhash_xyz")
    print(json.dumps(response, indent=4))
    print("="*65)