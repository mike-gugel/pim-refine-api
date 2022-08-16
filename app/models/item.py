from ormar.models import Model
from ormar import JSON, String, DateTime, UUID, Integer

from app.db import metadata, database, bdx_database

from sqlalchemy import func


class IceCatItemInfoModel(Model):
    class Meta:
        tablename = 'icecat_info'
        metadata = metadata
        database = database

    ean = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=13
        )
    info = JSON()
    requested_by = UUID()
    requested_at = DateTime(server_default=func.current_timestamp())


class CrawlabItemInfoModel(Model):
    class Meta:
        tablename = 'crawlab_info'
        metadata = metadata
        database = database

    ean = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=13,
        )
    info = JSON()
    task_id = UUID()


class PawInfoModel(Model):
    class Meta:
        tablename = 'paw_info'
        metadata = metadata
        database = database

    variant_id = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=15
        )
    info = JSON()

class PimQuery20_5(Model):
    class Meta:
        tablename = "PIM_query20_5"
        database = bdx_database
        metadata = metadata

    Variant_product = String(max_length=15, primary_key=True)
    Base_product = String(max_length=9, nullable=True)		
    EAN = String(max_length=13, nullable=True)
    Product_name = String(max_length=400, nullable=True)		
    SAP_name = String(max_length=120, nullable=True)	
    Mandators = String(max_length=90, nullable=True)
    Suppliers = String(max_length=350, nullable=True)
    Main_material_group = String(max_length=1, nullable=True)	
    KSP = String(max_length=2, nullable=True)	
    Material_group_subgroup = String(max_length=5, nullable=True)
    Material_group_node = String(max_length=5, nullable=True)
    Material_group = String(max_length=75, nullable=True)
    SAP_status = String(max_length=13, nullable=True)
    Approval = String(max_length=12, nullable=True)
    Status_data_maintenance = String(max_length=35, nullable=True)
    Flag_status = String(max_length=12, nullable=True)
    Online_reservation = String(max_length=3, nullable=True)
    Maintenance_classification = String(max_length=2, nullable=True)
    Processed_by_tool = String(max_length=5, nullable=True)
    Initial_responsibility = String(max_length=20, nullable=True)
    General_responsibility = String(max_length=20, nullable=True)
    Private_brand___brand = String(max_length=50, nullable=True)
    Product_line = String(max_length=50, nullable=True)
    Product_name_category = String(max_length=50, nullable=True)
    Type_designation = String(max_length=80, nullable=True)
    Description = String(max_length=10000, nullable=True)
    USP_1 = String(max_length=110, nullable=True)
    USP_2 = String(max_length=110, nullable=True)
    USP_3 = String(max_length=110, nullable=True)
    USP_4 = String(max_length=110, nullable=True)
    USP_5 = String(max_length=110, nullable=True)
    Name_attributes = String(max_length=150, nullable=True) # breaks when > original 125 
    Primary_frontend_category = String(max_length=8, nullable=True)
    Secondary_frontend_categories = String(max_length=110, nullable=True)
    Count_available_images = String(max_length=5, nullable=True)
    Count_active_images = String(max_length=5, nullable=True)
    URL_main_image = String(max_length=100, nullable=True)


class PimQuery29(Model):
    class Meta:
        tablename = "PIM_query29"
        database = bdx_database
        metadata = metadata
    
    id = Integer(primary_key=True)
    Material_group = String(max_length=60, nullable=True)
    Variant_product = String(max_length=60, nullable=True)
    Mandators = String(max_length=33, nullable=True)
    SAP_name = String(max_length=75, nullable=True)
    Product_name_category = String(max_length=110, nullable=True)
    Classifying_category = String(max_length=80, nullable=True)
    Attribute_identifier = String(max_length=80, nullable=True)
    Attribute_name = String(max_length=80, nullable=True)
    Attribute_type = String(max_length=9, nullable=True)
    Value_identifier = String(max_length=300, nullable=True)
    Value_name = String(max_length=300, nullable=True)
    Value_unit = String(max_length=60, nullable=True)
    Value_language = String(max_length=35, nullable=True)
