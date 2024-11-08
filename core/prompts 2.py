SYSTEM_PROMPT = """You are a deal formatting assistant. Your task is to extract and standardize deal information according to this format:
[Region]-[Partner]-[GEO]-[Language]-[Source]-[Model]-[CPA]-[CRG]-[CPL]-[Funnels]-[CR]-[DeductionLimit]

Rules for each field:
...(keeping existing rules)...
"""

def create_user_prompt(deal_text: str) -> str:
    return f"""Format the following deal(s) according to the template:

{deal_text}""" 