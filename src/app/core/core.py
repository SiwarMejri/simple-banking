from typing import Optional, Dict
from ..models import Account

accounts: Dict[str, Account] = {}

def reset_state():
    accounts.clear()

def get_account_balance(account_id: str) -> Optional[Account]:
    if account_id in accounts:
        return accounts[account_id]
    return None

def create_or_update_account(account_id: str, amount: int) -> Account:
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount)
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: int) -> Optional[Account]:
    if account_id not in accounts or accounts[account_id].balance < amount:
        return None
    accounts[account_id].balance -= amount
    return accounts[account_id]

def transfer_between_accounts(origin: str, destination: str, amount: int) -> (Optional[Account], Optional[Account]):
    if origin not in accounts or accounts[origin].balance < amount:
        return None, None  
    
    accounts[origin].balance -= amount
    
    if destination not in accounts:
        accounts[destination] = Account(id=destination, balance=0)  # create account with 0 balance if destination doesn't exist
    
    accounts[destination].balance += amount
    
    return accounts[origin], accounts[destination]

