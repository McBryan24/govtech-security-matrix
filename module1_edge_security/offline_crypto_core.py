import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class GovTechEdgeEncryptor:
    """
    Implements the Module 1 Technical Audit Criteria for WBG Digital ID deployments.
    Ensures zero-knowledge offline storage on field registration tablets.
    """
    def __init__(self):
        # In production, the public key is hardcoded onto the device; 
        # the private key remains locked in the Central Sovereign Server.
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.server_public_key = self.private_key.public_key()

    def encrypt_biometric_payload_offline(self, raw_biometric_template: bytes):
        """
        Encrypts raw PII at rest on the edge node using AES-256-GCM, 
        then wraps the symmetric key with the Server's RSA-2048 Public Key.
        """
        # 1. Generate a single-use symmetric key for AES-GCM
        aes_key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(aes_key)
        
        # 2. Generate a unique 12-byte initialization vector (nonce)
        nonce = os.urandom(12)
        
        # 3. Encrypt the raw biometric payload
        encrypted_payload = aesgcm.encrypt(nonce, raw_biometric_template, None)
        
        # 4. Wrap (encrypt) the AES key using the Server's Asymmetric Public Key
        wrapped_aes_key = self.server_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Return the secure package destined for eventual sync with central servers
        return {
            "nonce": nonce,
            "ciphertext": encrypted_payload,
            "wrapped_key": wrapped_aes_key
        }

    def verify_server_side_decryption(self, secure_package):
        """
        Simulates the Central Server using its private key to decrypt the payload,
        proving the 'Write-Only' edge architecture functions seamlessly.
        """
        # 1. Un-wrap the symmetric AES key using the secure server private key
        unwrapped_aes_key = self.private_key.decrypt(
            secure_package["wrapped_key"],
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 2. Decrypt the payload using the unwrapped key
        aesgcm = AESGCM(unwrapped_aes_key)
        decrypted_payload = aesgcm.decrypt(secure_package["nonce"], secure_package["ciphertext"], None)
        
        return decrypted_payload

# --- EXECUTE SIMULATION ---
if __name__ == "__main__":
    print("="*60)
    print(" INITIALIZING GOVTECH MODULE 1: EDGE-NODE FORENSIC SIMULATION ")
    print("="*60)
    
    encryptor = GovTechEdgeEncryptor()
    
    # Simulate a raw minuitiae fingerprint template captured in a rural district
    mock_fingerprint_data = b"FTR_TEMPLATE_MUTATION_VECTOR_APAC_88392X"
    print(f"[+] Raw Biometric Input Captured Offline: {mock_fingerprint_data.decode()}")
    
    # Execute edge encryption
    payload_package = encryptor.encrypt_biometric_payload_offline(mock_fingerprint_data)
    print("\n[~] Applying Asymmetric Cryptographic Wrapper...")
    print(f"    - AES-GCM Ciphertext (Hex): {payload_package['ciphertext'].hex()[:30]}...")
    print(f"    - Wrapped Symmetric Key (Hex): {payload_package['wrapped_key'].hex()[:30]}...")
    
    # Simulate data breach scenario
    print("\n[!] ATTACK VECTOR SIMULATION: Field Registration Tablet Stolen.")
    print("    - Device contains NO local private key.")
    print("    - Local ciphertext is computationally useless to adversary.")
    
    # Server-side verification
    decrypted_output = encryptor.verify_server_side_decryption(payload_package)
    print(f"\n[+] Central Server Sync Successful.")
    print(f"    - Decrypted Verification Payload: {decrypted_output.decode()}")
    print("="*60)