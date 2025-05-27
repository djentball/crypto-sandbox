def normalize_wallet_amount(wallet) -> bool:
    wallet.amount = round(wallet.amount, 8)
    return wallet.amount >= 1e-8
