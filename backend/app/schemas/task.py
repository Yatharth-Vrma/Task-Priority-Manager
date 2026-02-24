"""Pydantic schemas for API request/response validation."""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.task import Priority, Status


class TaskCreate(BaseModel):
    """Schema for creating a new task.
    
    Validates:
    - Title is not empty after trimming
    - Title length is within bounds
    - Description length is within bounds if provided
    - Priority is valid enum value
    - No extra/unknown fields accepted
    """
    model_config = ConfigDict(extra='forbid')

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Field(default=Priority.MEDIUM)
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty after stripping whitespace.
        
        Args:
            v: Title value
            
        Returns:
            Stripped title
            
        Raises:
            ValueError: If title is empty after stripping
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError('Title cannot be empty or whitespace')
        return stripped
    
    @field_validator('description')
    @classmethod
    def description_stripped(cls, v: Optional[str]) -> Optional[str]:
        """Strip description whitespace if provided.
        
        Args:
            v: Description value
            
        Returns:
            Stripped description or None
        """
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None


class TaskUpdate(BaseModel):
    """Schema for updating an existing task.
    
    All fields are optional to support partial updates.
    No extra/unknown fields accepted.
    """
    model_config = ConfigDict(extra='forbid')

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not empty if provided.
        
        Args:
            v: Title value
            
        Returns:
            Stripped title or None
            
        Raises:
            ValueError: If title is provided but empty after stripping
        """
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError('Title cannot be empty or whitespace')
            return stripped
        return None
    
    @field_validator('description')
    @classmethod
    def description_stripped(cls, v: Optional[str]) -> Optional[str]:
        """Strip description if provided.
        
        Args:
            v: Description value
            
        Returns:
            Stripped description or None
        """
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None


class StatusUpdate(BaseModel):
    """Schema for updating task status.
    
    Validates status is a valid enum value.
    Service layer enforces transition rules.
    No extra/unknown fields accepted.
    """
    model_config = ConfigDict(extra='forbid')

    status: Status


class TaskResponse(BaseModel):
    """Schema for task response.
    
    Represents the complete task state returned to clients.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    """Schema for error responses.
    
    Provides consistent error format across API.
    """
    error: str
    details: Optional[Any] = None
