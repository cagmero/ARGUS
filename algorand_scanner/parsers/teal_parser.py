"""
TEAL file parser for raw TEAL contracts
"""

import asyncio
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class TealParser:
    """Parser for TEAL files"""
    
    TEAL_OPCODES = {
        # Stack manipulation
        'int', 'byte', 'addr', 'arg', 'txn', 'global', 'load', 'store',
        # Arithmetic
        'add', 'sub', 'mul', 'div', 'mod', 'addw', 'mulw',
        # Logic
        'and', 'or', 'xor', 'not', 'shl', 'shr',
        # Comparison
        'eq', 'neq', 'lt', 'le', 'gt', 'ge',
        # Control flow
        'bnz', 'bz', 'b', 'return', 'assert', 'err', 'callsub', 'retsub',
        # Application state
        'app_global_get', 'app_global_put', 'app_local_get', 'app_local_put',
        'app_global_get_ex', 'app_local_get_ex', 'app_global_del', 'app_local_del',
        # Inner transactions
        'itxn_begin', 'itxn_field', 'itxn_submit', 'itxn_next',
        # Cryptographic
        'sha256', 'keccak256', 'sha512_256', 'ed25519verify', 'ecdsa_verify',
    }
    
    TEAL_FIELDS = {
        # Transaction fields
        'Sender', 'Fee', 'FirstValid', 'LastValid', 'Note', 'Lease', 'Receiver',
        'Amount', 'CloseRemainderTo', 'VotePK', 'SelectionPK', 'VoteFirst',
        'VoteLast', 'VoteKeyDilution', 'Type', 'TypeEnum', 'XferAsset',
        'AssetAmount', 'AssetSender', 'AssetReceiver', 'AssetCloseTo',
        'GroupIndex', 'TxID', 'ApplicationID', 'OnCompletion', 'ApplicationArgs',
        'NumAppArgs', 'Accounts', 'NumAccounts', 'ApprovalProgram', 'ClearStateProgram',
        'RekeyTo', 'ConfigAsset', 'ConfigAssetTotal', 'ConfigAssetDecimals',
        'ConfigAssetDefaultFrozen', 'ConfigAssetName', 'ConfigAssetURL',
        'ConfigAssetMetadataHash', 'ConfigAssetManager', 'ConfigAssetReserve',
        'ConfigAssetFreeze', 'ConfigAssetClawback', 'FreezeAsset', 'FreezeAssetAccount',
        'FreezeAssetFrozen',
        # Global fields
        'MinTxnFee', 'MinBalance', 'MaxTxnLife', 'ZeroAddress', 'GroupSize',
        'LogicSigVersion', 'Round', 'LatestTimestamp', 'CurrentApplicationID',
        'CreatorAddress', 'CurrentApplicationAddress', 'GroupID', 'OpcodeBudget',
        'CallerApplicationID', 'CallerApplicationAddress'
    }
    
    async def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse TEAL file and extract contract information"""
        try:
            content = await self._read_file(file_path)
            
            # Check if it's a valid TEAL file
            if not self._is_teal_file(content):
                return None
            
            lines = content.splitlines()
            
            # Extract TEAL information
            version = self._extract_version(lines)
            labels = self._extract_labels(lines)
            opcodes = self._extract_opcodes(lines)
            subroutines = self._extract_subroutines(lines)
            state_operations = self._extract_state_operations(lines)
            transaction_fields = self._extract_transaction_fields(lines)
            
            return {
                'file_path': str(file_path),
                'content': content,
                'lines': lines,
                'version': version,
                'labels': labels,
                'opcodes': opcodes,
                'subroutines': subroutines,
                'state_operations': state_operations,
                'transaction_fields': transaction_fields,
                'line_count': len(lines)
            }
            
        except Exception as e:
            logger.error(f"Error parsing TEAL file {file_path}: {e}")
            return None
    
    async def _read_file(self, file_path: Path) -> str:
        """Read file content asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, file_path.read_text, 'utf-8')
    
    def _is_teal_file(self, content: str) -> bool:
        """Check if content is a valid TEAL file"""
        lines = content.strip().splitlines()
        if not lines:
            return False
        
        # Check for TEAL version pragma
        first_line = lines[0].strip()
        if first_line.startswith('#pragma version'):
            return True
        
        # Check for common TEAL opcodes
        content_lower = content.lower()
        teal_indicators = ['txn ', 'global ', 'app_global_', 'int ', 'byte ', 'return', 'assert']
        return any(indicator in content_lower for indicator in teal_indicators)
    
    def _extract_version(self, lines: List[str]) -> Optional[int]:
        """Extract TEAL version from pragma"""
        for line in lines:
            line = line.strip()
            if line.startswith('#pragma version'):
                try:
                    version_str = line.split()[-1]
                    return int(version_str)
                except (IndexError, ValueError):
                    pass
        return None
    
    def _extract_labels(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract labels from TEAL code"""
        labels = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            # Labels end with ':'
            if line.endswith(':') and not line.startswith('//'):
                label_name = line[:-1].strip()
                if label_name and not any(char in label_name for char in [' ', '\t']):
                    labels.append({
                        'name': label_name,
                        'line': i
                    })
        
        return labels
    
    def _extract_opcodes(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract opcodes and their usage"""
        opcodes = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue
            
            # Skip labels
            if line.endswith(':'):
                continue
            
            # Extract opcode (first word)
            parts = line.split()
            if parts:
                opcode = parts[0].lower()
                if opcode in self.TEAL_OPCODES:
                    opcodes.append({
                        'opcode': opcode,
                        'line': i,
                        'full_instruction': line,
                        'args': parts[1:] if len(parts) > 1 else []
                    })
        
        return opcodes
    
    def _extract_subroutines(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract subroutine definitions and calls"""
        subroutines = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip().lower()
            
            # Subroutine calls
            if 'callsub' in line:
                parts = line.split()
                if len(parts) >= 2:
                    subroutines.append({
                        'type': 'call',
                        'name': parts[1],
                        'line': i
                    })
            
            # Subroutine returns
            elif 'retsub' in line:
                subroutines.append({
                    'type': 'return',
                    'line': i
                })
        
        return subroutines
    
    def _extract_state_operations(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract application state operations"""
        state_ops = []
        
        state_opcodes = [
            'app_global_get', 'app_global_put', 'app_global_del', 'app_global_get_ex',
            'app_local_get', 'app_local_put', 'app_local_del', 'app_local_get_ex'
        ]
        
        for i, line in enumerate(lines, 1):
            line_lower = line.strip().lower()
            
            for opcode in state_opcodes:
                if opcode in line_lower:
                    state_ops.append({
                        'operation': opcode,
                        'line': i,
                        'instruction': line.strip()
                    })
                    break
        
        return state_ops
    
    def _extract_transaction_fields(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract transaction field accesses"""
        tx_fields = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Look for txn/gtxn field accesses
            if re.search(r'\b(txn|gtxn)\s+\w+', line, re.IGNORECASE):
                parts = line.split()
                if len(parts) >= 2:
                    field_name = parts[1]
                    if field_name in self.TEAL_FIELDS:
                        tx_fields.append({
                            'type': parts[0].lower(),  # txn or gtxn
                            'field': field_name,
                            'line': i,
                            'instruction': line
                        })
        
        return tx_fields