from pydantic import BaseModel
from typing import List, Optional, Tuple


class Txt2ImgParams(BaseModel):
    pos: str
    neg: str = ""
    width: int = 512
    height: int = 512
    batch: int = 1
    steps: int = 20
    cfg: float = 7
    seed: int = -1
    sampler: str = "euler"
    scheduler: str = "normal"
    checkpoint: str = "dreamshaper_8.safetensors"
    vae: Optional[str] = None
    loras: List[Tuple[str, float]] = []


class Img2ImgParams(Txt2ImgParams):
    image: str
    denoise: float


class LinkedTo(BaseModel):
    type: str
    id: str


class Verification(BaseModel):
    status: str
    strategy: str
    attempts: Optional[int]
    expire_at: Optional[int]
    error: Optional[dict]


class EmailAddress(BaseModel):
    id: str
    object: str
    email_address: str
    reserved: bool
    verification: Verification
    linked_to: List[LinkedTo]


class ExternalAccount(BaseModel):
    object: str
    id: str
    google_id: Optional[str]
    approved_scopes: Optional[str]
    email_address: str
    given_name: str
    family_name: str
    picture: Optional[str]
    username: Optional[str]
    public_metadata: dict
    label: Optional[str]
    verification: Verification


class User(BaseModel):
    id: str
    object: str
    username: str
    first_name: str
    last_name: str
    image_url: str
    has_image: bool
    primary_email_address_id: str
    primary_phone_number_id: Optional[str]
    primary_web3_wallet_id: Optional[str]
    password_enabled: bool
    two_factor_enabled: bool
    totp_enabled: bool
    backup_code_enabled: bool
    email_addresses: List[EmailAddress]
    phone_numbers: List[
        dict
    ]  # Assuming phone_numbers is a list of dictionaries, adjust as needed
    web3_wallets: List[
        dict
    ]  # Assuming web3_wallets is a list of dictionaries, adjust as needed
    external_accounts: List[ExternalAccount]
    saml_accounts: List[
        dict
    ]  # Assuming saml_accounts is a list of dictionaries, adjust as needed
    public_metadata: dict
    private_metadata: dict
    unsafe_metadata: dict
    external_id: Optional[str]
    last_sign_in_at: int
    banned: bool
    locked: bool
    lockout_expires_in_seconds: Optional[int]
    verification_attempts_remaining: int
    created_at: int
    updated_at: int
    delete_self_enabled: bool
    create_organization_enabled: bool
    last_active_at: int
    profile_image_url: str
