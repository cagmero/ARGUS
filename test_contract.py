from algopy import ARC4Contract, UInt64, String, Txn, Global

class TestContract(ARC4Contract):
    balance: UInt64
    
    def __init__(self) -> None:
        self.balance = UInt64(1000)
    
    @abimethod()
    def unsafe_withdraw(self, amount: UInt64) -> None:
        # CRITICAL: Missing access control
        self.balance -= amount  # MEDIUM: Unchecked arithmetic
        
    @abimethod() 
    def get_random(self) -> UInt64:
        # HIGH: Weak randomness
        return Global.latest_timestamp % 100