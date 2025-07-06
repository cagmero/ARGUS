"""
Vulnerable Algorand Smart Contract (PyTeal/Algopy)
This contract contains INTENTIONAL vulnerabilities for testing purposes
DO NOT USE IN PRODUCTION
"""

from algopy import ARC4Contract, UInt64, String, Txn, Global, op, Bytes
from algopy.arc4 import abimethod

class VulnerableContract(ARC4Contract):
    """A deliberately vulnerable contract for security testing"""
    
    # State variables
    balance: UInt64
    owner: String
    secret_key: String
    admin_backdoor: String
    
    def __init__(self) -> None:
        # VULNERABILITY 1: Hardcoded sensitive data
        self.secret_key = String("sk_live_51234567890abcdef")  # CRITICAL: Hardcoded private key
        self.admin_backdoor = String("ADMIN123BACKDOOR456")    # HIGH: Hardcoded backdoor
        self.balance = UInt64(1000000)
        self.owner = Global.creator_address
    
    @abimethod()
    def withdraw(self, amount: UInt64) -> None:
        """VULNERABILITY 2: Missing access control - CRITICAL"""
        # Anyone can withdraw funds - no authorization check
        self.balance -= amount  # VULNERABILITY 3: Unchecked arithmetic - MEDIUM
        
    @abimethod()
    def emergency_withdraw(self) -> None:
        """VULNERABILITY 4: Logic bomb with hardcoded condition - HIGH"""
        # Backdoor for specific address
        if Txn.sender == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA":
            self.balance = UInt64(0)  # Drain all funds
            op.exit(1)  # VULNERABILITY 5: Unsafe exit operation - LOW
    
    @abimethod()
    def get_random_winner(self) -> UInt64:
        """VULNERABILITY 6: Weak randomness source - HIGH"""
        # Using predictable timestamp for randomness
        random_value = Global.latest_timestamp % 100
        return random_value
    
    @abimethod()
    def unsafe_transfer(self, to_address: String, amount: UInt64) -> None:
        """VULNERABILITY 7: Missing input validation - MEDIUM"""
        # No validation of parameters
        # No check if amount > balance
        # No validation of to_address format
        self.balance -= amount
        # Transfer logic would go here
    
    @abimethod()
    def process_batch(self, iterations: UInt64) -> None:
        """VULNERABILITY 8: Resource exhaustion / Infinite loop - HIGH"""
        i = UInt64(0)
        # Unbounded loop - can cause DoS
        while i < iterations:  # No upper limit check
            self.balance += 1
            # Missing increment - potential infinite loop
            # i += 1  # This line is commented out!
    
    @abimethod()
    def get_user_balance(self, user: String) -> UInt64:
        """VULNERABILITY 9: Unsafe state access - MEDIUM"""
        # Direct state access without existence check
        # This could fail if user doesn't exist in local state
        return UInt64(0)  # Simplified for demo
    
    @abimethod()
    def admin_function(self, new_owner: String) -> None:
        """VULNERABILITY 10: Timestamp dependency - MEDIUM"""
        # Using timestamp for critical business logic
        if Global.latest_timestamp % 2 == 0:  # Manipulable condition
            self.owner = new_owner
    
    @abimethod()
    def calculate_reward(self, base_amount: UInt64, multiplier: UInt64) -> UInt64:
        """VULNERABILITY 11: Integer overflow potential - MEDIUM"""
        # No bounds checking on multiplication
        result = base_amount * multiplier  # Could overflow
        return result
    
    @abimethod()
    def divide_funds(self, divisor: UInt64) -> UInt64:
        """VULNERABILITY 12: Division by zero - MEDIUM"""
        # No check for zero divisor
        result = self.balance / divisor  # Could cause division by zero
        return result
    
    @abimethod()
    def reentrancy_vulnerable(self, external_contract: UInt64) -> None:
        """VULNERABILITY 13: Reentrancy vulnerability - HIGH"""
        # State change after external call
        # In real implementation, this would make external call first
        # then update state, allowing reentrancy attacks
        self.balance -= 100  # State change should be before external call
        # external_call(external_contract)  # Simulated external call
    
    @abimethod()
    def time_locked_function(self) -> None:
        """VULNERABILITY 14: Timestamp manipulation - MEDIUM"""
        # Critical function depends on exact timestamp
        if Global.latest_timestamp == 1640995200:  # Specific timestamp
            self.balance = UInt64(0)  # Dangerous operation
    
    @abimethod()
    def update_contract(self, new_approval_program: Bytes) -> None:
        """VULNERABILITY 15: Insecure upgrade mechanism - CRITICAL"""
        # No access control for contract updates
        # Anyone can update the contract
        pass  # Update logic would go here
    
    @abimethod()
    def debug_function(self, debug_mode: UInt64) -> String:
        """VULNERABILITY 16: Information disclosure - LOW"""
        if debug_mode == 1:
            # Exposing sensitive internal state
            return self.secret_key  # Leaking sensitive data
        return String("OK")
    
    @abimethod()
    def batch_process_unlimited(self, data: String) -> None:
        """VULNERABILITY 17: No rate limiting - MEDIUM"""
        # No limits on batch processing
        # Could be used for DoS attacks
        for i in range(1000000):  # Hardcoded large number
            # Expensive operation
            pass
    
    @abimethod()
    def legacy_function(self) -> None:
        """VULNERABILITY 18: Dead/unreachable code - LOW"""
        return  # Early return makes code below unreachable
        
        # Dead code below
        self.balance += 1000
        self.owner = String("DEAD_CODE")
    
    @abimethod()
    def weak_validation(self, amount: UInt64, signature: String) -> None:
        """VULNERABILITY 19: Weak cryptographic validation - HIGH"""
        # Weak signature validation
        if len(signature) > 0:  # Insufficient validation
            self.balance += amount
    
    @abimethod()
    def race_condition_vulnerable(self, amount: UInt64) -> None:
        """VULNERABILITY 20: Race condition - MEDIUM"""
        # Check-then-act pattern vulnerable to race conditions
        current_balance = self.balance
        # Time gap here allows race conditions
        if current_balance >= amount:
            self.balance = current_balance - amount