"""
Service for managing custom dental status definitions.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from ..database.database import db_manager
from ..database.models import CustomStatus

logger = logging.getLogger(__name__)


class CustomStatusService:
    """Service for managing custom dental status definitions."""
    
    def create_custom_status(self, status_data: Dict[str, Any]) -> Optional[CustomStatus]:
        """
        Create a new custom status definition.
        
        Args:
            status_data: Dictionary containing status data
            
        Returns:
            Created CustomStatus object or None if failed
        """
        try:
            session = db_manager.get_session()
            
            # Check if status_name already exists
            existing = session.query(CustomStatus).filter(
                CustomStatus.status_name == status_data.get('status_name')
            ).first()
            
            if existing:
                session.close()
                logger.warning(f"Custom status '{status_data.get('status_name')}' already exists")
                return None
            
            custom_status = CustomStatus(
                status_name=status_data.get('status_name'),
                status_code=status_data.get('status_code', status_data.get('status_name')),  # Use status_name as fallback
                display_name=status_data.get('display_name', status_data.get('status_name')),
                description=status_data.get('description', ''),
                color=status_data.get('color', '#808080'),
                color_code=status_data.get('color_code', status_data.get('color', '#808080')),  # Set color_code
                category=status_data.get('category', 'custom'),
                is_active=status_data.get('is_active', True),
                sort_order=status_data.get('sort_order', 0),
                icon_name=status_data.get('icon_name', ''),
                created_by=status_data.get('created_by') if isinstance(status_data.get('created_by'), int) else None
            )
            
            session.add(custom_status)
            session.commit()
            
            status_id = custom_status.id
            session.close()
            
            logger.info(f"Created custom status '{status_data.get('status_name')}' with ID {status_id}")
            return self.get_custom_status_by_id(status_id)
            
        except Exception as e:
            logger.error(f"Error creating custom status: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def get_custom_status_by_id(self, status_id: int) -> Optional[Dict[str, Any]]:
        """
        Get custom status by ID.
        
        Args:
            status_id: ID of the custom status
            
        Returns:
            Dictionary containing custom status data or None if not found
        """
        try:
            session = db_manager.get_session()
            
            status = session.query(CustomStatus).filter(
                CustomStatus.id == status_id
            ).first()
            
            if not status:
                session.close()
                return None
            
            result = {
                'id': status.id,
                'status_name': status.status_name,
                'display_name': status.display_name,
                'description': status.description,
                'color': status.color,
                'category': status.category,
                'is_active': status.is_active,
                'sort_order': status.sort_order,
                'icon_name': status.icon_name,
                'created_by': status.created_by,
                'created_at': status.created_at,
                'updated_at': status.updated_at
            }
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting custom status {status_id}: {str(e)}")
            if session:
                session.close()
            return None
    
    def get_custom_status_by_name(self, status_name: str) -> Optional[Dict[str, Any]]:
        """
        Get custom status by name.
        
        Args:
            status_name: Name of the custom status
            
        Returns:
            Dictionary containing custom status data or None if not found
        """
        try:
            session = db_manager.get_session()
            
            status = session.query(CustomStatus).filter(
                CustomStatus.status_name == status_name
            ).first()
            
            session.close()
            
            if not status:
                return None
            
            return {
                'id': status.id,
                'status_name': status.status_name,
                'display_name': status.display_name,
                'description': status.description,
                'color': status.color,
                'category': status.category,
                'is_active': status.is_active,
                'sort_order': status.sort_order,
                'icon_name': status.icon_name,
                'created_by': status.created_by,
                'created_at': status.created_at,
                'updated_at': status.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting custom status by name '{status_name}': {str(e)}")
            if session:
                session.close()
            return None
    
    def get_all_custom_statuses(self, category: Optional[str] = None, 
                               is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get all custom status definitions.
        
        Args:
            category: Optional category filter
            is_active: Optional active status filter
            
        Returns:
            List of custom status dictionaries
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(CustomStatus)
            
            if category:
                query = query.filter(CustomStatus.category == category)
            
            if is_active is not None:
                query = query.filter(CustomStatus.is_active == is_active)
            
            statuses = query.order_by(CustomStatus.sort_order, CustomStatus.display_name).all()
            
            results = []
            for status in statuses:
                results.append({
                    'id': status.id,
                    'status_name': status.status_name,
                    'display_name': status.display_name,
                    'description': status.description,
                    'color': status.color,
                    'category': status.category,
                    'is_active': status.is_active,
                    'sort_order': status.sort_order,
                    'icon_name': status.icon_name,
                    'created_by': status.created_by,
                    'created_at': status.created_at,
                    'updated_at': status.updated_at
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting custom statuses: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_statuses_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get custom statuses grouped by category.
        
        Returns:
            Dictionary mapping categories to lists of status dictionaries
        """
        try:
            all_statuses = self.get_all_custom_statuses(is_active=True)
            
            categories = {}
            for status in all_statuses:
                category = status['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(status)
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting statuses by category: {str(e)}")
            return {}
    
    def update_custom_status(self, status_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update a custom status definition.
        
        Args:
            status_id: ID of the status to update
            update_data: Dictionary containing fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            status = session.query(CustomStatus).filter(CustomStatus.id == status_id).first()
            
            if not status:
                session.close()
                return False
            
            # Check if status_name is being changed and doesn't conflict
            if 'status_name' in update_data and update_data['status_name'] != status.status_name:
                existing = session.query(CustomStatus).filter(
                    CustomStatus.status_name == update_data['status_name']
                ).first()
                
                if existing:
                    session.close()
                    logger.warning(f"Custom status name '{update_data['status_name']}' already exists")
                    return False
            
            # Update allowed fields
            allowed_fields = [
                'status_name', 'display_name', 'description', 'color', 'category',
                'is_active', 'sort_order', 'icon_name'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(status, field, update_data[field])
            
            status.updated_at = datetime.now()
            session.commit()
            session.close()
            
            logger.info(f"Updated custom status {status_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating custom status {status_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def delete_custom_status(self, status_id: int) -> bool:
        """
        Delete a custom status definition.
        Note: This will also remove the status from any dental chart records.
        
        Args:
            status_id: ID of the status to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            status = session.query(CustomStatus).filter(CustomStatus.id == status_id).first()
            
            if not status:
                session.close()
                return False
            
            # Note: In a production system, you might want to check if this status
            # is being used in any dental chart records and handle that appropriately
            
            session.delete(status)
            session.commit()
            session.close()
            
            logger.info(f"Deleted custom status {status_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting custom status {status_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def toggle_status_active(self, status_id: int) -> bool:
        """
        Toggle the active status of a custom status.
        
        Args:
            status_id: ID of the status to toggle
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            status = session.query(CustomStatus).filter(CustomStatus.id == status_id).first()
            
            if not status:
                session.close()
                return False
            
            status.is_active = not status.is_active
            status.updated_at = datetime.now()
            session.commit()
            session.close()
            
            logger.info(f"Toggled active status for custom status {status_id} to {status.is_active}")
            return True
            
        except Exception as e:
            logger.error(f"Error toggling active status for {status_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def search_custom_statuses(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search custom statuses by name or description.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching custom status dictionaries
        """
        try:
            session = db_manager.get_session()
            
            search_pattern = f'%{search_term}%'
            
            statuses = session.query(CustomStatus).filter(
                or_(
                    CustomStatus.status_name.ilike(search_pattern),
                    CustomStatus.display_name.ilike(search_pattern),
                    CustomStatus.description.ilike(search_pattern)
                )
            ).order_by(CustomStatus.display_name).all()
            
            results = []
            for status in statuses:
                results.append({
                    'id': status.id,
                    'status_name': status.status_name,
                    'display_name': status.display_name,
                    'description': status.description,
                    'color': status.color,
                    'category': status.category,
                    'is_active': status.is_active,
                    'sort_order': status.sort_order,
                    'icon_name': status.icon_name,
                    'created_by': status.created_by,
                    'created_at': status.created_at,
                    'updated_at': status.updated_at
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching custom statuses: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_predefined_statuses(self) -> List[Dict[str, str]]:
        """
        Get predefined dental status options (the 51 comprehensive statuses).
        These are not stored in the database but are used as defaults.
        
        Returns:
            List of predefined status dictionaries
        """
        predefined_statuses = [
            # Healthy/Normal States
            {"status_name": "normal", "status_code": "NORM", "display_name": "Normal", "category": "healthy", "color": "#00FF00"},
            {"status_name": "healthy", "status_code": "HLTH", "display_name": "Healthy", "category": "healthy", "color": "#32CD32"},
            {"status_name": "sound", "status_code": "SOND", "display_name": "Sound", "category": "healthy", "color": "#90EE90"},
            
            # Decay/Caries
            {"status_name": "initial_caries", "status_code": "IC", "display_name": "Initial Caries", "category": "decay", "color": "#FFD700"},
            {"status_name": "superficial_caries", "status_code": "SC", "display_name": "Superficial Caries", "category": "decay", "color": "#FFA500"},
            {"status_name": "moderate_caries", "status_code": "MC", "display_name": "Moderate Caries", "category": "decay", "color": "#FF8C00"},
            {"status_name": "deep_caries", "status_code": "DC", "display_name": "Deep Caries", "category": "decay", "color": "#FF4500"},
            {"status_name": "extensive_caries", "status_code": "EC", "display_name": "Extensive Caries", "category": "decay", "color": "#DC143C"},
            {"status_name": "rampant_caries", "status_code": "RC", "display_name": "Rampant Caries", "category": "decay", "color": "#8B0000"},
            
            # Restorations
            {"status_name": "amalgam_filling", "status_code": "AF", "display_name": "Amalgam Filling", "category": "restoration", "color": "#708090"},
            {"status_name": "composite_filling", "status_code": "CF", "display_name": "Composite Filling", "category": "restoration", "color": "#F5F5DC"},
            {"status_name": "gold_filling", "status_code": "GF", "display_name": "Gold Filling", "category": "restoration", "color": "#FFD700"},
            {"status_name": "ceramic_filling", "status_code": "CERF", "display_name": "Ceramic Filling", "category": "restoration", "color": "#FFFAF0"},
            {"status_name": "temporary_filling", "status_code": "TF", "display_name": "Temporary Filling", "category": "restoration", "color": "#DDA0DD"},
            {"status_name": "defective_restoration", "status_code": "DR", "display_name": "Defective Restoration", "category": "restoration", "color": "#CD853F"},
            
            # Crowns/Caps
            {"status_name": "porcelain_crown", "status_code": "PC", "display_name": "Porcelain Crown", "category": "prosthetic", "color": "#E6E6FA"},
            {"status_name": "metal_crown", "status_code": "MC", "display_name": "Metal Crown", "category": "prosthetic", "color": "#C0C0C0"},
            {"status_name": "porcelain_fused_metal", "status_code": "PFM", "display_name": "Porcelain Fused to Metal", "category": "prosthetic", "color": "#D3D3D3"},
            {"status_name": "gold_crown", "status_code": "GC", "display_name": "Gold Crown", "category": "prosthetic", "color": "#DAA520"},
            {"status_name": "zirconia_crown", "status_code": "ZC", "display_name": "Zirconia Crown", "category": "prosthetic", "color": "#F8F8FF"},
            
            # Endodontic Treatment
            {"status_name": "root_canal_treatment", "status_code": "RCT", "display_name": "Root Canal Treatment", "category": "endodontic", "color": "#FF69B4"},
            {"status_name": "pulp_cap", "status_code": "PCAP", "display_name": "Pulp Cap", "category": "endodontic", "color": "#FFB6C1"},
            {"status_name": "pulpotomy", "status_code": "PULP", "display_name": "Pulpotomy", "category": "endodontic", "color": "#FFC0CB"},
            {"status_name": "apexification", "status_code": "APEX", "display_name": "Apexification", "category": "endodontic", "color": "#FFCCCB"},
            
            # Periodontal Conditions
            {"status_name": "gingivitis", "status_code": "GING", "display_name": "Gingivitis", "category": "periodontal", "color": "#FF6347"},
            {"status_name": "periodontitis", "status_code": "PERIO", "display_name": "Periodontitis", "category": "periodontal", "color": "#B22222"},
            {"status_name": "pocket_formation", "status_code": "POCK", "display_name": "Pocket Formation", "category": "periodontal", "color": "#CD5C5C"},
            {"status_name": "gum_recession", "status_code": "GR", "display_name": "Gum Recession", "category": "periodontal", "color": "#F08080"},
            {"status_name": "bone_loss", "status_code": "BL", "display_name": "Bone Loss", "category": "periodontal", "color": "#8B0000"},
            
            # Extractions/Missing
            {"status_name": "extracted", "status_code": "EXT", "display_name": "Extracted", "category": "missing", "color": "#000000"},
            {"status_name": "missing", "status_code": "MISS", "display_name": "Missing", "category": "missing", "color": "#2F2F2F"},
            {"status_name": "congenitally_missing", "status_code": "CM", "display_name": "Congenitally Missing", "category": "missing", "color": "#696969"},
            {"status_name": "impacted", "status_code": "IMP", "display_name": "Impacted", "category": "missing", "color": "#A9A9A9"},
            {"status_name": "unerupted", "status_code": "UNER", "display_name": "Unerupted", "category": "missing", "color": "#808080"},
            
            # Prosthetic Replacements
            {"status_name": "implant", "status_code": "IMPL", "display_name": "Implant", "category": "prosthetic", "color": "#4169E1"},
            {"status_name": "bridge_abutment", "status_code": "BA", "display_name": "Bridge Abutment", "category": "prosthetic", "color": "#6495ED"},
            {"status_name": "bridge_pontic", "status_code": "BP", "display_name": "Bridge Pontic", "category": "prosthetic", "color": "#87CEEB"},
            {"status_name": "partial_denture", "status_code": "PD", "display_name": "Partial Denture", "category": "prosthetic", "color": "#87CEFA"},
            {"status_name": "full_denture", "status_code": "FD", "display_name": "Full Denture", "category": "prosthetic", "color": "#B0E0E6"},
            
            # Orthodontic
            {"status_name": "orthodontic_bracket", "status_code": "OB", "display_name": "Orthodontic Bracket", "category": "orthodontic", "color": "#9370DB"},
            {"status_name": "space_maintainer", "status_code": "SM", "display_name": "Space Maintainer", "category": "orthodontic", "color": "#DDA0DD"},
            {"status_name": "retainer", "status_code": "RET", "display_name": "Retainer", "category": "orthodontic", "color": "#EE82EE"},
            
            # Trauma/Fractures
            {"status_name": "fracture", "status_code": "FRAC", "display_name": "Fracture", "category": "trauma", "color": "#FF0000"},
            {"status_name": "luxation", "status_code": "LUX", "display_name": "Luxation", "category": "trauma", "color": "#DC143C"},
            {"status_name": "avulsion", "status_code": "AVUL", "display_name": "Avulsion", "category": "trauma", "color": "#B22222"},
            
            # Developmental Anomalies
            {"status_name": "supernumerary", "status_code": "SUPER", "display_name": "Supernumerary", "category": "anomaly", "color": "#FF1493"},
            {"status_name": "malformed", "status_code": "MAL", "display_name": "Malformed", "category": "anomaly", "color": "#DB7093"},
            {"status_name": "enamel_defect", "status_code": "ED", "display_name": "Enamel Defect", "category": "anomaly", "color": "#C71585"},
            
            # Treatment Planned
            {"status_name": "treatment_planned", "status_code": "TP", "display_name": "Treatment Planned", "category": "planned", "color": "#00CED1"},
            {"status_name": "needs_evaluation", "status_code": "NE", "display_name": "Needs Evaluation", "category": "planned", "color": "#48D1CC"},
            {"status_name": "observation", "status_code": "OBS", "display_name": "Under Observation", "category": "planned", "color": "#40E0D0"},
            
            # Other Conditions
            {"status_name": "sensitive", "status_code": "SENS", "display_name": "Sensitive", "category": "other", "color": "#FFFF00"},
            {"status_name": "wear", "status_code": "WEAR", "display_name": "Wear/Attrition", "category": "other", "color": "#BDB76B"},
            {"status_name": "stain", "status_code": "STAIN", "display_name": "Stain/Discoloration", "category": "other", "color": "#D2691E"}
        ]
        
        return predefined_statuses
    
    def initialize_predefined_statuses(self) -> bool:
        """
        Initialize the database with predefined dental statuses.
        Only adds statuses that don't already exist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            predefined = self.get_predefined_statuses()
            created_count = 0
            
            for status_data in predefined:
                existing = self.get_custom_status_by_name(status_data['status_name'])
                if not existing:
                    result = self.create_custom_status(status_data)
                    if result:
                        created_count += 1
            
            logger.info(f"Initialized {created_count} predefined statuses")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing predefined statuses: {str(e)}")
            return False
    
    def initialize_default_statuses(self) -> bool:
        """
        Initialize default dental statuses (alias for initialize_predefined_statuses).
        
        Returns:
            True if successful, False otherwise
        """
        return self.initialize_predefined_statuses()
    
    def add_custom_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a custom status (wrapper for create_custom_status with success response).
        
        Args:
            status_data: Dictionary containing status data
            
        Returns:
            Dictionary with 'success' status and created status data
        """
        try:
            status = self.create_custom_status(status_data)
            
            if status:
                return {
                    'success': True,
                    'status': status,
                    'message': 'Custom status created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create custom status'
                }
                
        except Exception as e:
            logger.error(f"Error adding custom status: {str(e)}")
            return {
                'success': False,
                'error': f'Error adding custom status: {str(e)}'
            }


# Global service instance
custom_status_service = CustomStatusService()
