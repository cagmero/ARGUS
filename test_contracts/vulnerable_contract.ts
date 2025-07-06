/**
 * Vulnerable Algorand TypeScript Contract Integration
 * This file contains INTENTIONAL vulnerabilities for testing purposes
 * DO NOT USE IN PRODUCTION
 */

import algosdk from 'algosdk';
import { Algodv2, Transaction, makeApplicationCallTxnFromObject, makePaymentTxnWithSuggestedParamsFromObject } from 'algosdk';

// VULNERABILITY 1: Hardcoded sensitive credentials - CRITICAL
const HARDCODED_PRIVATE_KEY = "your-private-key-here-do-not-hardcode";  // CRITICAL
const HARDCODED_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about";  // CRITICAL
const ADMIN_SECRET = "admin123secret456";  // HIGH

// VULNERABILITY 2: Hardcoded network configuration - MEDIUM
const ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const ALGOD_SERVER = "http://localhost";
const ALGOD_PORT = 4001;

// VULNERABILITY 3: Insecure random number generation - HIGH
function generateInsecureRandom(): number {
    return Math.random();  // Weak randomness source
}

// VULNERABILITY 4: Weak session token generation - HIGH
function generateSessionToken(): string {
    return Math.random().toString(36).substring(7);  // Predictable
}

class VulnerableAlgorandContract {
    private algodClient: Algodv2;
    private appId: number;
    
    constructor(appId: number) {
        // VULNERABILITY 5: No input validation - MEDIUM
        this.appId = appId;  // Should validate appId is positive number
        
        // VULNERABILITY 6: Insecure client configuration - MEDIUM
        this.algodClient = new Algodv2(ALGOD_TOKEN, ALGOD_SERVER, ALGOD_PORT);
    }
    
    // VULNERABILITY 7: Missing access control - CRITICAL
    async adminWithdraw(amount: number): Promise<string> {
        // No authentication or authorization checks
        return await this.withdraw(amount);
    }
    
    // VULNERABILITY 8: Unchecked arithmetic operations - MEDIUM
    async withdraw(amount: number): Promise<string> {
        // No bounds checking
        const balance = await this.getBalance();
        const newBalance = balance - amount;  // Could go negative
        
        // VULNERABILITY 9: Missing error handling - MEDIUM
        const suggestedParams = await this.algodClient.getTransactionParams().do();
        
        // VULNERABILITY 10: Unsigned transaction vulnerability - MEDIUM
        const txn = makeApplicationCallTxnFromObject({
            from: "SENDER_ADDRESS_HERE",  // VULNERABILITY 11: Hardcoded address
            appIndex: this.appId,
            onComplete: algosdk.OnApplicationComplete.NoOpOC,
            appArgs: [new Uint8Array(Buffer.from("withdraw")), new Uint8Array(Buffer.from(amount.toString()))],
            suggestedParams
        });
        
        // VULNERABILITY 12: Transaction not signed before submission
        // Should sign transaction before sending
        
        return "transaction_id_placeholder";
    }
    
    // VULNERABILITY 13: Direct state access without validation - LOW
    async getBalance(): Promise<number> {
        try {
            const accountInfo = await this.algodClient.accountInformation("ACCOUNT_ADDRESS").do();
            return accountInfo.amount;
        } catch (error) {
            // VULNERABILITY 14: Information disclosure in error messages - LOW
            console.log("Error getting balance:", error);  // Logs sensitive info
            return 0;
        }
    }
    
    // VULNERABILITY 15: SQL injection equivalent (unsafe string concatenation) - HIGH
    async searchTransactions(userInput: string): Promise<any> {
        // Unsafe string concatenation for API calls
        const query = `transactions?address=${userInput}`;  // No sanitization
        // In real scenario, this could lead to API injection
        return null;
    }
    
    // VULNERABILITY 16: Race condition vulnerability - MEDIUM
    private isProcessing = false;
    
    async processTransaction(amount: number): Promise<void> {
        // Check-then-act race condition
        if (this.isProcessing) {
            throw new Error("Already processing");
        }
        
        // Time gap here allows race conditions
        await new Promise(resolve => setTimeout(resolve, 100));
        
        this.isProcessing = true;
        // Process transaction
        this.isProcessing = false;
    }
    
    // VULNERABILITY 17: Weak cryptographic validation - HIGH
    validateSignature(message: string, signature: string): boolean {
        // Weak validation - just checks if signature exists
        return signature.length > 0;  // Insufficient validation
    }
    
    // VULNERABILITY 18: Timestamp dependency vulnerability - MEDIUM
    async timeBasedOperation(): Promise<boolean> {
        const currentTime = Date.now();
        
        // Critical logic depends on exact timestamp
        if (currentTime % 1000 === 0) {  // Manipulable condition
            return true;
        }
        
        return false;
    }
    
    // VULNERABILITY 19: Resource exhaustion / DoS vulnerability - HIGH
    async batchProcess(items: any[]): Promise<void> {
        // No limit on batch size
        for (const item of items) {  // Could process millions of items
            await this.expensiveOperation(item);
        }
    }
    
    private async expensiveOperation(item: any): Promise<void> {
        // Simulated expensive operation
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // VULNERABILITY 20: Information disclosure - MEDIUM
    async getDebugInfo(): Promise<any> {
        return {
            privateKey: HARDCODED_PRIVATE_KEY,  // Exposing sensitive data
            adminSecret: ADMIN_SECRET,
            internalState: this.getInternalState()
        };
    }
    
    private getInternalState(): any {
        return {
            appId: this.appId,
            processingStatus: this.isProcessing
        };
    }
    
    // VULNERABILITY 21: Insecure deserialization - HIGH
    async processUserData(serializedData: string): Promise<void> {
        try {
            // Unsafe deserialization
            const userData = JSON.parse(serializedData);  // No validation
            await this.processTransaction(userData.amount);
        } catch (error) {
            // Swallow errors silently
        }
    }
    
    // VULNERABILITY 22: Missing rate limiting - MEDIUM
    async publicEndpoint(data: any): Promise<void> {
        // No rate limiting - can be spammed
        await this.processUserData(JSON.stringify(data));
    }
    
    // VULNERABILITY 23: Weak session management - HIGH
    private sessions: Map<string, any> = new Map();
    
    createSession(userId: string): string {
        const sessionId = generateSessionToken();  // Weak token generation
        this.sessions.set(sessionId, {
            userId,
            createdAt: Date.now(),
            // VULNERABILITY 24: No session expiration
        });
        return sessionId;
    }
    
    // VULNERABILITY 25: Missing input sanitization - MEDIUM
    async logUserAction(action: string, details: string): Promise<void> {
        // No sanitization of log data
        console.log(`User action: ${action}, Details: ${details}`);  // Log injection possible
    }
    
    // VULNERABILITY 26: Insecure random for critical operations - HIGH
    generateTransactionNonce(): string {
        return Math.random().toString();  // Predictable nonce
    }
    
    // VULNERABILITY 27: Missing HTTPS enforcement - MEDIUM
    async makeInsecureRequest(url: string): Promise<any> {
        // No HTTPS enforcement
        const response = await fetch(url);  // Could be HTTP
        return response.json();
    }
    
    // VULNERABILITY 28: Weak password validation - MEDIUM
    validatePassword(password: string): boolean {
        return password.length > 3;  // Weak password requirements
    }
    
    // VULNERABILITY 29: Missing CORS protection - LOW
    setupAPIEndpoint(): void {
        // In a real Express.js setup, this would be:
        // app.use(cors({ origin: '*' }));  // Overly permissive CORS
    }
    
    // VULNERABILITY 30: Insufficient logging - LOW
    async criticalOperation(): Promise<void> {
        // No logging of critical operations
        await this.withdraw(1000000);
    }
}

// VULNERABILITY 31: Global state pollution - LOW
let globalAppInstance: VulnerableAlgorandContract;

// VULNERABILITY 32: Unsafe global functions - MEDIUM
function unsafeGlobalWithdraw(amount: number): Promise<string> {
    // No validation of global state
    return globalAppInstance.withdraw(amount);
}

// VULNERABILITY 33: Memory leak potential - LOW
const eventListeners: Function[] = [];

function addListener(callback: Function): void {
    eventListeners.push(callback);
    // No cleanup mechanism for listeners
}

// VULNERABILITY 34: Prototype pollution potential - HIGH
function mergeObjects(target: any, source: any): any {
    for (const key in source) {
        if (key === '__proto__') {
            // VULNERABILITY: Should prevent prototype pollution
            target[key] = source[key];
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

// VULNERABILITY 35: Unsafe eval usage - CRITICAL
function executeUserCode(code: string): any {
    // NEVER do this in production
    return eval(code);  // Code injection vulnerability
}

// Export vulnerable contract
export default VulnerableAlgorandContract;

// VULNERABILITY 36: Exposed sensitive configuration
export const CONFIG = {
    PRIVATE_KEY: HARDCODED_PRIVATE_KEY,
    ADMIN_SECRET: ADMIN_SECRET,
    DATABASE_URL: "mongodb://admin:password123@localhost:27017/vulnerable_db"
};