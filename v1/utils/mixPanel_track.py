from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Optional
from typing import Optional, Dict
from datetime import date
from mixpanel import Mixpanel
from user_agents import parse
import uvicorn
import os
from dotenv import load_dotenv

from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging


load_dotenv()

MIXPANEL_TOKEN = os.getenv('MIXPANEL_TOKEN')

class EventTracker:
    def __init__(self, mixpanel_token: str):
        """
        Initialize the Mixpanel event tracker.
        
        :param mixpanel_token: Your Mixpanel project token
        """
        self.mp = Mixpanel(mixpanel_token)
        self.user_agent_parser = UserAgentParser()

    def _get_device_details(self, user_agent_string: str) -> Dict:
        """
        Parse device details from user agent string.
        
        :param user_agent_string: User agent string to parse
        :return: Dictionary of device details
        """
        try:
            user_agent = parse(user_agent_string)
            return {
                "browser_family": user_agent.browser.family,
                "browser_version": user_agent.browser.version_string,
                "is_mobile": user_agent.is_mobile,
                "is_tablet": user_agent.is_tablet,
                "is_pc": user_agent.is_pc,
                "is_bot": user_agent.is_bot,
                "$os": user_agent.os.family,
                "os_version": user_agent.os.version_string,
                "device_family": user_agent.device.family,
                "device_brand": user_agent.device.brand,
                "device_model": user_agent.device.model
            }
        except Exception:
            return {}

    def track_event(
        self, 
        user_id: str, 
        event_name: str = 'Translation',
        event_data_properties: Optional[Dict] = None, 
        user_agent_string: Optional[str] = None):
        """
        Track an event in Mixpanel with optional device details.
        
        :param user_id: Unique identifier for the user
        :param event_name: Name of the event to track (default: 'Translation')
        :param event_data: Dictionary of additional event properties
        :param user_agent_string: Optional user agent string for device parsing
        """
        # Prepare base properties
        properties = event_data_properties or {}
        
        # Add device details if user agent is provided
        if user_agent_string:
            device_details = self._get_device_details(user_agent_string)
            properties.update(device_details)
        
        # Track event in Mixpanel
        try:
            self.mp.track(user_id, event_name, properties)
            print(f"Event tracked: {event_name}")
        except Exception as e:
            print(f"Error tracking event: {e}")

    
    def track_user_signup(
        self, 
        user_id: str, 
        event_name: str = 'Signup',
        event_data_properties: Optional[Dict] = None, 
        user_agent_string: Optional[str] = None):
        """
        Track an event in Mixpanel with optional device details.
        
        :param user_id: Unique identifier for the user
        :param event_name: Name of the event to track (default: 'Translation')
        :param event_data: Dictionary of additional event properties
        :param user_agent_string: Optional user agent string for device parsing
        """
        # Prepare base properties
        properties = event_data_properties or {}
        
        # Add device details if user agent is provided
        if user_agent_string:
            device_details = self._get_device_details(user_agent_string)
            properties.update(device_details)
        
        # Track event in Mixpanel
        try:
            self.mp.people_set(user_id, properties)
            print(f"Added new user: {event_name}")
            self.mp.track(user_id, event_name, properties)
            print(f"Event tracked: {event_name}")
        except Exception as e:
            print(f"Error tracking event: {e}")

class UserAgentParser:
    def parse_user_agent(self, user_agent_string: str):
        """
        Parse user agent string using user-agents library.
        
        :param user_agent_string: User agent string to parse
        :return: Parsed user agent object
        """
        return parse(user_agent_string)

# Example Usage
def create_mixpanel_tracker(mixpanel_token: str):
    """
    Create and return an EventTracker instance.
    
    :param mixpanel_token: Your Mixpanel project token
    :return: EventTracker instance
    """
    return EventTracker(mixpanel_token)



# ##############################################################
# ##################### FastAPI Application ####################

class EventRequest(BaseModel):
    user_id: Optional[str] = None
    type: Optional[str] = 'Translation'

    input: Optional[str] = ""
    output: Optional[str] = ""
    input_lang: Optional[str] = None
    output_lang: Optional[str] = None
    
    ip_address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    response_time: Optional[float] = None
    version: str = '1.0.0'
    source_app: Optional[str] = None


class SignupRequest(BaseModel):
    user_id: Optional[str] = None
    type: Optional[str] = 'Signup'
    email: Optional[str] = None
    
    gender: Optional[str] = None
    profession: Optional[str] = None
    interest: Optional[str] = None
    # birth_date: Optional[date] = None
    birth_date: Optional[int] = None
    
    ip_address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    response_time: Optional[float] = None
    version: str = '1.0.0'
    source_app: Optional[str] = None



################################################################################


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DictToClass:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

class TrackingResponse(BaseModel):
    """Response model for tracking operations"""
    status_code: int = 200
    success: bool
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


def track_user_input(event_data_dict, request: Request) -> TrackingResponse:
    """
    Track a user event with device information
    
    Args:
        event_data (EventRequest): Event data model
        request (Request): FastAPI request object
    
    Returns:
        TrackingResponse: Standardized response object
    
    Raises:
        HTTPException: For various tracking-related errors
    """
    try:
        # Initialize the tracker
        tracker = create_mixpanel_tracker(MIXPANEL_TOKEN)
        event_data = DictToClass(event_data_dict)
        logger.info(f"Tracker created for user_id: {event_data.user_id}")

        # Prepare event properties
        event_properties = {
            "input": event_data.input,
            "output": event_data.output,
            "input_lang": event_data.input_lang,
            "output_lang": event_data.output_lang,
            "response_time": event_data.response_time,
            "version": event_data.version,
            "source_app": event_data.source_app,
            "ip_address": event_data.ip_address,
            "$city": event_data.city,
            "$Country": event_data.country,
            "model": event_data.model,
            "is_stream": event_data.is_stream,
        }

        # Track the event
        event_result = tracker.track_event(
            user_id=event_data.user_id,
            event_name=event_data.type,
            event_data_properties=event_properties,
            user_agent_string=request.headers.get('User-Agent')
        )
        
        # Return successful response
        return TrackingResponse(
            status_code = 200,
            success=True,
            message="Event tracked successfully",
            timestamp=datetime.utcnow(),
            details={
                "user_id": event_data.user_id,
                "event_type": event_data.type,
                "source_app": event_data.source_app
            }
        )

    except ConnectionError as e:
        logger.error(f"Connection error while tracking event: {str(e)}")
        # raise HTTPException(
        #     status_code=503,
        #     detail="Unable to connect to tracking service"
        # )
        return TrackingResponse(
            status_code = 503,
            success=False,
            message="Unable to connect to tracking service",
            timestamp=datetime.utcnow(),
            details={
                "user_id": event_data.user_id,
                "event_type": event_data.type,
                "source_app": event_data.source_app
            }
        )
    
    except ValueError as e:
        logger.error(f"Invalid data error: {str(e)}")
        # raise HTTPException(
        #     status_code=400,
        #     detail=f"Invalid event data: {str(e)}"
        # )
        
        return TrackingResponse(
            status_code = 400,
            success=False,
            message=f"Invalid event data: {str(e)}",
            timestamp=datetime.utcnow(),
            details={
                "user_id": event_data.user_id,
                "event_type": event_data.type,
                "source_app": event_data.source_app
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error while tracking event: {str(e)}")
        # raise HTTPException(
        #     status_code=500,
        #     detail="Internal server error during event tracking"
        # )
        return TrackingResponse(
            status_code = 500,
            success=False,
            message="Internal server error during event tracking",
            timestamp=datetime.utcnow(),
            details={
                "user_id": event_data.user_id,
                "event_type": event_data.type,
                "source_app": event_data.source_app
            }
        )


def track_signup_input(signup_data_dict, request: Request) -> TrackingResponse:
    """
    Track a signup event with device information
    
    Args:
        signup_data (SignupRequest): Signup data model
        request (Request): FastAPI request object
    
    Returns:
        TrackingResponse: Standardized response object
    
    Raises:
        HTTPException: For various tracking-related errors
    """
    try:
        # Initialize the tracker
        tracker = create_mixpanel_tracker(MIXPANEL_TOKEN)
        print(type(signup_data_dict))
        signup_data = DictToClass(signup_data_dict)
        # Prepare signup properties
        signup_properties = {
            "gender": signup_data.gender,
            "age": signup_data.birth_date,
            "profession": signup_data.profession,
            "response_time": signup_data.response_time,
            "version": signup_data.version,
            "source_app": signup_data.source_app,
            "ip_address": signup_data.ip_address,
            "$city": signup_data.city,
            "$Country": signup_data.country,
        }

        # Track the signup
        signup_result = tracker.track_user_signup(
            user_id=str(signup_data.id),
            event_name=signup_data.type,
            event_data_properties=signup_properties,
            user_agent_string=request.headers.get('User-Agent')
        )

        # Return successful response
        return TrackingResponse(
            status_code = 200,
            success=True,
            message="Signup event tracked successfully",
            timestamp=datetime.utcnow(),
            details={
                "user_id": str(signup_data.id),
                "source_app": signup_data.source_app
            }
        )

    except ConnectionError as e:
        logger.error(f"Connection error while tracking signup: {str(e)}")
        # raise HTTPException(
        #     status_code=503,
        #     detail="Unable to connect to tracking service"
        # )
        
        return TrackingResponse(
            status_code = 503,
            success=False,
            message="Unable to connect to tracking service",
            timestamp=datetime.utcnow(),
            details={
            }
        )
    
    except ValueError as e:
        logger.error(f"Invalid signup data error: {str(e)}")
        # raise HTTPException(
        #     status_code=400,
        #     detail=f"Invalid signup data: {str(e)}"
        # )
        
        return TrackingResponse(
            status_code = 400,
            success=False,
            message=f"Invalid signup data error: {str(e)}",
            timestamp=datetime.utcnow(),
            details={
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error while tracking signup: {str(e)}")
        # raise HTTPException(
        #     status_code=500,
        #     detail="Internal server error during signup tracking"
        # )
        
        return TrackingResponse(
            status_code = 500,
            success=False,
            message="Internal server error during signup tracking",
            timestamp=datetime.utcnow(),
            details={
            }
        )

