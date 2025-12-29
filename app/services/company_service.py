from sqlalchemy.orm import Session
from app.models.company import Company
from uuid import UUID, uuid4
from app.services.s3_service import s3_service
from typing import Optional, List
from app.models.admin import Admin

class CompanyService:
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

            logo_filename = None
            if file_data and filename and content_type:
                file_ext = filename.split('.')[-1] if '.' in filename else 'png'
                logo_filename = f"companies/{db_company.id}/logo/{uuid4().hex}.{file_ext}"

                logo_url = s3_service.upload_file(file_data, logo_filename, content_type)

                if not logo_url:
                    raise Exception("Failed to upload logo to S3")
                
                db_company.logo_url = logo_url

            if current_user["role"] == "admin":
                from app.models.admin import Admin
                admin = Admin(user_id=current_user["id"], company_id=db_company.id)
                db.add(admin)

            db.commit()
            db.refresh(db_company)
            return db_company

        except Exception as e:
            db.rollback()
            
            # Hapus file dari S3 jika ada error
            if logo_filename:
                try:
                    s3_service.delete_file(logo_filename)
                except Exception as s3_error:
                    print(f"Warning: Failed to delete logo during rollback: {s3_error}")
            
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

            # Update data company
            for key, value in company_data.items():
                if value is not None:
                    setattr(db_company, key, value)

            # Handle logo upload jika ada
            new_logo_filename = None
            if file_data and filename and content_type:
                file_ext = filename.split('.')[-1] if '.' in filename else 'png'
                new_logo_filename = f"companies/{db_company.id}/logo/{uuid4().hex}.{file_ext}"

                logo_url = s3_service.upload_file(file_data, new_logo_filename, content_type)

                if not logo_url:
                    raise Exception("Failed to upload new logo to S3")

                # Hapus semua logo lama dari S3 berdasarkan prefix
                try:
                    old_files = s3_service.list_files_by_prefix(f"companies/{db_company.id}/logo/")
                    for old_file in old_files:
                        if old_file != new_logo_filename:  # Jangan hapus file yang baru di-upload
                            s3_service.delete_file(old_file)
                except Exception as e:
                    print(f"Warning: Failed to delete old logo files: {e}")

                db_company.logo_url = logo_url

            db.commit()
            db.refresh(db_company)
            return db_company

        except Exception as e:
            db.rollback()
            
            # Hapus file baru dari S3 jika ada error
            if new_logo_filename:
                try:
                    s3_service.delete_file(new_logo_filename)
                except Exception as s3_error:
                    print(f"Warning: Failed to delete logo during rollback: {s3_error}")
            
            raise e

    def list_companies(self, db: Session, skip: int = 0, limit: int = 10) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()