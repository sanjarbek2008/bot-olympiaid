from typing import List, Dict, Any, Optional
from config.database import get_supabase_client
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseManager:
    @staticmethod
    async def get_upcoming_olympiads() -> List[Dict[str, Any]]:
        """Fetch upcoming olympiads from Supabase"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("olympiads").select("*").eq("status", "upcoming").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching olympiads: {e}")
            return []

    @staticmethod
    async def get_olympiad_by_id(olympiad_id: str) -> Optional[Dict[str, Any]]:
        """Get specific olympiad by ID"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("olympiads").select("*").eq("id", olympiad_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching olympiad {olympiad_id}: {e}")
            return None

    @staticmethod
    async def check_email_exists(email: str) -> Optional[Dict[str, Any]]:
        """Check if email exists in profiles table"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("profiles").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error checking email {email}: {e}")
            return None

    @staticmethod
    async def check_existing_registration(user_id: str, olympiad_id: str) -> bool:
        """Check if user is already registered for this olympiad"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("olympiad_participants").select("id").eq("user_id", user_id).eq("olympiad_id",
                                                                                                      olympiad_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking existing registration: {e}")
            return False

    @staticmethod
    async def register_for_olympiad(
            olympiad_id: str,
            user_id: str,
            passport_id: str,
            date_of_birth: str,
            gender: str,
            country: str,
            city: str,
            heard_about_us: str,
            has_participated_before: bool
    ) -> bool:
        """Register user for an olympiad"""
        try:
            supabase = get_supabase_client()

            # Check if already registered
            if await SupabaseManager.check_existing_registration(user_id, olympiad_id):
                return False

            # Create registration
            registration_data = {
                "id": str(uuid.uuid4()),
                "olympiad_id": olympiad_id,
                "user_id": user_id,
                "status": "approved",
                "role": "participant",
                "passport_id": passport_id,
                "certificate_url": None,
                "date_of_birth": date_of_birth,
                "gender": gender,
                "country": country,
                "city": city,
                "heard_about_us": heard_about_us,
                "has_participated_before": has_participated_before,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            response = supabase.table("olympiad_participants").insert(registration_data).execute()
            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Error registering user for olympiad: {e}")
            return False

    @staticmethod
    async def get_olympiad_price(olympiad_id: str) -> int:
        """Get olympiad price in points"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("olympiads").select("price").eq("id", olympiad_id).execute()
            return response.data[0]["price"] if response.data else 0
        except Exception as e:
            logger.error(f"Error getting olympiad price: {e}")
            return 0

    @staticmethod
    async def get_olympiad_registrations_count(olympiad_id: str) -> int:
        """Get current number of registrations for olympiad"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("olympiad_participants").select("id", count="exact").eq("olympiad_id",
                                                                                              olympiad_id).execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error getting registrations count: {e}")
            return 0

    @staticmethod
    async def get_olympiad_limit(olympiad_id: str) -> Optional[int]:
        """Get olympiad registration limit"""
        try:
            supabase = get_supabase_client()
            response = supabase.table("olympiads").select("registration_limit").eq("id", olympiad_id).execute()
            return response.data[0]["registration_limit"] if response.data else None
        except Exception as e:
            logger.error(f"Error getting olympiad limit: {e}")
            return None

    @staticmethod
    def get_supabase_client():
        """Get Supabase client instance"""
        return get_supabase_client()