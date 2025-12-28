from sqlalchemy.orm import Session
from app.models.company import Company
from uuid import UUID, uuid4
from app.services.s3_service import s3_service
from typing import Optional, List
from app.models.admin import Admin

class CompanyService:
    def __init__(self):
        self.s3_service = s3_service

    def create_company_from_form(self, db: Session, company_data: dict, file_data: bytes = None, filename: str = None, content_type: str = None, current_user: dict = None) -> Company:
        if current_user["role"] not in ["admin"]:
            raise Exception("Unauthorized: Only admin can create company")

        if current_user["role"] == "admin":
            from app.models.admin import Admin
            admin = db.query(Admin).filter(Admin.user_id == current_user["id"]).first()
            if admin:
                raise Exception("Admin already has a company assigned")

        try:
            db_company = Company(**company_data)
            db.add(db_company)
            db.flush()

            logo_uploaded = False
            if file_data and filename and content_type:
                file_ext = filename.split('.')[-1] if '.' in filename else 'png'
                logo_filename = f"companies/{db_company.id}/logo/{uuid4().hex}.{file_ext}"

                logo_url = self.s3_service.upload_file(file_data, logo_filename, content_type)

                if logo_url:
                    db_company.logo_url = logo_url
                    logo_uploaded = True

            if current_user["role"] == "admin":
                from app.models.admin import Admin
                admin = Admin(user_id=current_user["id"], company_id=db_company.id)
                db.add(admin)

            db.commit()
            return db_company

        except Exception as e:
            db.rollback()
            
            if 'logo_filename' in locals() and logo_uploaded:
                try:
                    self.s3_service.delete_file(logo_filename)
                except Exception as s3_error:
                    print(f"Error deleting uploaded logo during rollback: {s3_error}")
            
            raise e

    def get_company_by_id(self, db: Session, company_id: UUID) -> Optional[Company]:
        return db.query(Company).filter(Company.id == company_id).first()
    
    def get_company_by_admin_id(self, db: Session, current_user: dict) -> Optional[Company]:
        if current_user["role"] != "admin":
            raise Exception("Unauthorized: Only admin can access their company")

        from app.models.admin import Admin
        admin = db.query(Admin).filter(Admin.user_id == current_user["id"]).first()
        if not admin:
            return None

        return db.query(Company).filter(Company.id == admin.company_id).first()

    def update_company_from_form(self, db: Session, company_data: dict, file_data: bytes = None, filename: str = None, content_type: str = None, current_user: dict = None) -> Optional[Company]:
        if current_user["role"] not in ["admin"]:
            raise Exception("Unauthorized: Only admin can update company information")

        try:
            admin = db.query(Admin).filter(Admin.user_id == current_user["id"]).first()
            if not admin:
                raise Exception("Admin does not have a company assigned")

            db_company = db.query(Company).filter(Company.id == admin.company_id).first()
            if not db_company:
                return None

            old_logo_url = db_company.logo_url

            for key, value in company_data.items():
                if value is not None:
                    setattr(db_company, key, value)

            new_logo_uploaded = False
            if file_data and filename and content_type:
                if db_company.logo_url:
                    try:
                        old_logo_key = db_company.logo_url.split('/')[-2] + '/' + db_company.logo_url.split('/')[-1]
                        self.s3_service.delete_file(old_logo_key)
                    except Exception as e:
                        print(f"Error deleting old logo: {e}")

                file_ext = filename.split('.')[-1] if '.' in filename else 'png'
                logo_filename = f"companies/{db_company.id}/logo/{uuid4().hex}.{file_ext}"

                logo_url = self.s3_service.upload_file(file_data, logo_filename, content_type)

                if logo_url:
                    db_company.logo_url = logo_url
                    new_logo_uploaded = True

            db.commit()
            db.refresh(db_company)
            return db_company

        except Exception as e:
            db.rollback()
            
            if 'new_logo_uploaded' in locals() and new_logo_uploaded and 'logo_filename' in locals():
                try:
                    self.s3_service.delete_file(logo_filename)
                except Exception as s3_error:
                    print(f"Error deleting uploaded logo during rollback: {s3_error}")
            
            raise e

    def list_companies(self, db: Session, skip: int = 0, limit: int = 10) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()