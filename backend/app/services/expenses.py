from collections import defaultdict

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.models.models import Expense, User
from app.schemas.expenses import (
    ExpenseCreate, ExpenseUpdate, ExpenseOut,
    ExpenseSummary, CategorySummary, MonthlyExpense,
    TotalSpendData, CategoryBreakdownItem, CategoryTrendMonth,
    SpendTrendData, TopTransactionData
)
from app.repositories.expense_repository import ExpenseRepository
from app.utils.upload import upload_receipt_image
from typing import Optional
from datetime import datetime, timedelta
import calendar
import json
import csv
import io
from uuid import UUID


class ExpenseService:
    @staticmethod
    def _expense_to_response(expense: Expense) -> dict:
        expense_dict = ExpenseOut.model_validate(expense).model_dump()
        if expense.tags:
            if isinstance(expense.tags, str):
                try:
                    expense_dict["tags"] = json.loads(expense.tags)
                except json.JSONDecodeError:
                    expense_dict["tags"] = []
            else:
                expense_dict["tags"] = expense.tags
        else:
            expense_dict["tags"] = []
        return expense_dict

    
    @staticmethod
    def get_expenses(
        db: Session, 
        user: User, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> dict:
        """Get expenses with filters and pagination"""
        repo = ExpenseRepository(db)
        expenses, total_count = repo.list_expenses(
            user.id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            page=page,
            limit=limit,
        )

        expense_list = [ExpenseService._expense_to_response(expense) for expense in expenses]
        
        return {
            "success": True,
            "data": expense_list,
            "message": f"Retrieved {len(expense_list)} expenses",
            "meta": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
    
    @staticmethod
    def create_expense(db: Session, user: User, expense_data: ExpenseCreate) -> dict:
        """Create a new expense"""
        repo = ExpenseRepository(db)
        try:
            expense = repo.create_expense(user.id, expense_data)
            expense_out = ExpenseOut.model_validate(expense)
            return {
                "success": True,
                "data": expense_out,
                "message": "Expense created successfully"
            }
        except Exception as e:
            repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create expense: {str(e)}"
            )
    
    @staticmethod
    def get_expense(db: Session, user: User, expense_id: UUID) -> dict:
        """Get specific expense by ID"""
        repo = ExpenseRepository(db)
        expense = repo.get_expense_for_user(expense_id, user.id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        expense_out = ExpenseOut.model_validate(expense)
        return {
            "success": True,
            "data": expense_out,
            "message": "Expense retrieved successfully"
        }
    
    @staticmethod
    def update_expense(db: Session, user: User, expense_id: UUID, expense_data: ExpenseUpdate) -> dict:
        """Update an expense"""
        repo = ExpenseRepository(db)
        expense = repo.get_expense_for_user(expense_id, user.id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        try:
            update_data = expense_data.model_dump(exclude_unset=True)
            updated_expense = repo.update_expense(expense, update_data)
            expense_out = ExpenseOut.model_validate(updated_expense)
            return {
                "success": True,
                "data": expense_out,
                "message": "Expense updated successfully"
            }
        except Exception as e:
            repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update expense: {str(e)}"
            )
    
    @staticmethod
    def delete_expense(db: Session, user: User, expense_id: UUID) -> dict:
        """Delete an expense"""
        repo = ExpenseRepository(db)
        expense = repo.get_expense_for_user(expense_id, user.id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        try:
            expense_out = ExpenseOut.model_validate(expense)
            repo.delete_expense(expense)
            return {
                "success": True,
                "data": expense_out,
                "message": "Expense deleted successfully"
            }
        except Exception as e:
            repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete expense"
            )
    
    @staticmethod
    def get_expense_summary(
        db: Session, 
        user: User, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get expense summary with category breakdown"""
        repo = ExpenseRepository(db)
        expenses = repo.list_in_period(
            user.id,
            start_date=start_date,
            end_date=end_date,
        )

        if not expenses:
            return {
                "success": True,
                "data": {
                    "total_amount": 0.0,
                    "total_count": 0,
                    "average_amount": 0.0,
                    "categories": [],
                    "period_start": start_date or datetime.min,
                    "period_end": end_date or datetime.max
                },
                "message": "No expenses found for the specified period"
            }
        
        # Calculate totals
        total_amount = sum(expense.amount for expense in expenses)
        total_count = len(expenses)
        average_amount = total_amount / total_count if total_count > 0 else 0
        
        # Group by category
        category_data = {}
        for expense in expenses:
            category = expense.category
            if category not in category_data:
                category_data[category] = {"amount": 0.0, "count": 0}
            category_data[category]["amount"] += expense.amount
            category_data[category]["count"] += 1
        
        # Create category summaries
        categories = []
        for category, data in category_data.items():
            categories.append(CategorySummary(
                category=category,
                total_amount=data["amount"],
                count=data["count"],
                percentage=round((data["amount"] / total_amount) * 100, 2) if total_amount > 0 else 0
            ))
        
        # Sort by amount descending
        categories.sort(key=lambda x: x.total_amount, reverse=True)
        
        summary = ExpenseSummary(
            total_amount=total_amount,
            total_count=total_count,
            average_amount=round(average_amount, 2),
            categories=categories,
            period_start=start_date or min(expense.date for expense in expenses),
            period_end=end_date or max(expense.date for expense in expenses)
        )
        
        return {
            "success": True,
            "data": summary,
            "message": "Expense summary retrieved successfully"
        }
    
    @staticmethod
    def get_categories_summary(db: Session, user: User) -> dict:
        """Get expense categories with totals"""
        repo = ExpenseRepository(db)
        categories = repo.get_category_totals(user.id)

        total_amount = sum(float(cat.total_amount) for cat in categories)

        category_summaries = []
        for cat in categories:
            total = float(cat.total_amount)
            category_summaries.append(CategorySummary(
                category=cat.category,
                total_amount=total,
                count=cat.count,
                percentage=round((total / total_amount) * 100, 2) if total_amount > 0 else 0
            ))
        
        # Sort by amount descending
        category_summaries.sort(key=lambda x: x.total_amount, reverse=True)
        
        return {
            "success": True,
            "data": category_summaries,
            "message": "Categories retrieved successfully"
        }
    
    @staticmethod
    def get_monthly_expenses(db: Session, user: User, year: int, month: int) -> dict:
        """Get expenses for specific month"""
        repo = ExpenseRepository(db)
        expenses = repo.get_monthly_expenses(user.id, year, month)
        
        if not expenses:
            return {
                "success": True,
                "data": {
                    "year": year,
                    "month": month,
                    "total_amount": 0.0,
                    "count": 0,
                    "categories": []
                },
                "message": f"No expenses found for {month}/{year}"
            }
        
        # Calculate totals
        total_amount = sum(expense.amount for expense in expenses)
        count = len(expenses)
        
        # Group by category
        category_data = {}
        for expense in expenses:
            category = expense.category
            if category not in category_data:
                category_data[category] = {"amount": 0.0, "count": 0}
            category_data[category]["amount"] += expense.amount
            category_data[category]["count"] += 1
        
        # Create category summaries
        categories = []
        for category, data in category_data.items():
            categories.append(CategorySummary(
                category=category,
                total_amount=data["amount"],
                count=data["count"],
                percentage=round((data["amount"] / total_amount) * 100, 2) if total_amount > 0 else 0
            ))
        
        monthly_expense = MonthlyExpense(
            year=year,
            month=month,
            total_amount=total_amount,
            count=count,
            categories=categories
        )
        
        return {
            "success": True,
            "data": monthly_expense,
            "message": f"Monthly expenses for {month}/{year} retrieved successfully"
        }
    
    @staticmethod
    async def upload_receipt(db: Session, user: User, expense_id: UUID, file: UploadFile) -> dict:
        """Upload receipt for expense"""
        repo = ExpenseRepository(db)
        expense = repo.get_expense_for_user(expense_id, user.id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        try:
            # Upload receipt image
            receipt_url = await upload_receipt_image(file)
            
            # Update expense with receipt URL
            updated_expense = repo.set_receipt_url(expense, receipt_url)
            expense_out = ExpenseOut.model_validate(updated_expense)
            return {
                "success": True,
                "data": expense_out,
                "message": "Receipt uploaded successfully"
            }
        except Exception as e:
            repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload receipt: {str(e)}"
            )
    
    @staticmethod
    def get_recurring_expenses(db: Session, user: User) -> dict:
        """Get recurring expenses"""
        repo = ExpenseRepository(db)
        expenses = repo.get_recurring_expenses(user.id)
        expense_list = [ExpenseOut.model_validate(expense) for expense in expenses]
        
        return {
            "success": True,
            "data": expense_list,
            "message": f"Retrieved {len(expense_list)} recurring expenses"
        }
    
    # @staticmethod
    # def bulk_import_expenses(db: Session, user: User, bulk_data: ExpenseBulkImport) -> dict:
    #     """Bulk import expenses"""
    #     try:
    #         created_expenses = []
            
    #         for expense_data in bulk_data.expenses:
    #             tags_json = json.dumps(expense_data.tags) if expense_data.tags else None
                
    #             expense = Expense(
    #                 user_id=user.id,
    #                 amount=expense_data.amount,
    #                 currency=expense_data.currency,
    #                 category=expense_data.category,
    #                 subcategory=expense_data.subcategory,
    #                 merchant=expense_data.merchant,
    #                 description=expense_data.description,
    #                 date=expense_data.date,
    #                 payment_method=expense_data.payment_method,
    #                 is_recurring=expense_data.is_recurring,
    #                 recurrence_rule=expense_data.recurrence_rule,
    #                 tags=tags_json
    #             )
                
    #             db.add(expense)
    #             created_expenses.append(expense)
            
    #         db.commit()
            
    #         # Refresh all expenses
    #         for expense in created_expenses:
    #             db.refresh(expense)
            
    #         expense_list = [ExpenseOut.model_validate(expense) for expense in created_expenses]
            
    #         return {
    #             "success": True,
    #             "data": expense_list,
    #             "message": f"Successfully imported {len(expense_list)} expenses"
    #         }
    #     except Exception as e:
    #         db.rollback()
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Failed to import expenses: {str(e)}"
    #         )
    
    @staticmethod
    def export_expenses(
        db: Session, 
        user: User, 
        format: str = "csv",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Export expenses to CSV or JSON"""
        repo = ExpenseRepository(db)
        expenses = repo.list_for_export(
            user.id,
            start_date=start_date,
            end_date=end_date,
        )
        
        if format.lower() == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Amount', 'Currency', 'Category', 'Subcategory', 
                'Merchant', 'Description', 'Date', 'Payment Method', 
                'Is Recurring', 'Tags', 'Created At'
            ])
            
            # Write data
            for expense in expenses:
                tags = []
                if expense.tags:
                    if isinstance(expense.tags, str):
                        try:
                            tags = json.loads(expense.tags)
                        except json.JSONDecodeError:
                            tags = []
                    else:
                        tags = expense.tags
                writer.writerow([
                    str(expense.id), expense.amount, expense.currency,
                    expense.category, expense.subcategory or '', 
                    expense.merchant or '', expense.description or '',
                    expense.date.isoformat(), expense.payment_method or '',
                    expense.is_recurring, ', '.join(tags),
                    expense.created_at.isoformat()
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "success": True,
                "data": csv_content,
                "message": f"Exported {len(expenses)} expenses to CSV"
            }
        else:
            # Return JSON
            expense_list = [ExpenseOut.model_validate(expense) for expense in expenses]
            return {
                "success": True,
                "data": expense_list,
                "message": f"Exported {len(expenses)} expenses to JSON"
            }
        


# ------------------------------------ AI-powered methods ------------------------------------
    @staticmethod
    async def parse_text_with_ai(db: Session, user: User, text: str) -> dict:
        """Parse expense from natural language text using AI"""
        from app.services.ai_service import ai_service
        
        try:
            # Parse with AI
            parsed_data = await ai_service.parse_text_expense(text)
            
            # Check if the input is not expense-related
            if not parsed_data.get('is_expense_related', True):
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": None,
                    "confidence": 0,
                    "message": parsed_data.get('message', 'Please provide a valid expense description. For example: "I spent 500 taka on lunch at KFC" or "Bought groceries for 1200 taka".')
                }
            
            if parsed_data.get('confidence', 0) < 0.5:
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": parsed_data,
                    "confidence": parsed_data.get('confidence', 0),
                    "message": "Low confidence in parsing. Please provide more details about your expense (amount, what you bought, where, etc.)."
                }
            
            # Create expense from parsed data
            expense_create = ExpenseCreate(
                amount=parsed_data['amount'],
                currency=parsed_data.get('currency', 'Taka'),
                category=parsed_data['category'],
                subcategory=parsed_data.get('subcategory'),
                merchant=parsed_data.get('merchant'),
                description=parsed_data.get('description'),
                date=datetime.fromisoformat(parsed_data['date']),
                payment_method=parsed_data.get('payment_method'),
                tags=parsed_data.get('tags', [])
            )
            
            # Create the expense
            result = ExpenseService.create_expense(db, user, expense_create)
            
            return {
                "success": True,
                "data": result['data'],
                "parsed_data": parsed_data,
                "confidence": parsed_data.get('confidence', 0.8),
                "message": "Expense created successfully from text"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "parsed_data": None,
                "confidence": 0,
                "message": f"Error parsing text: {str(e)}"
            }
    
    @staticmethod
    async def parse_receipt_with_ai(db: Session, user: User, image_file: UploadFile) -> dict:
        """Parse expense from receipt image using AI"""
        from app.services.ai_service import ai_service
        repo = ExpenseRepository(db)

        try:
            # Parse with AI
            parsed_data = await ai_service.parse_receipt_image(image_file)
            
            if parsed_data.get('confidence', 0) < 0.5:
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": parsed_data,
                    "confidence": parsed_data.get('confidence', 0),
                    "message": "Low confidence in receipt parsing. Please verify the image quality."
                }
            
            # Upload receipt image (optional - for storage)
            receipt_url = None
            try:
                # Reset file pointer
                await image_file.seek(0)
                receipt_url = await upload_receipt_image(image_file)
            except:
                pass  # Continue without receipt URL if upload fails
            
            # Create expense from parsed data
            expense_create = ExpenseCreate(
                amount=parsed_data['amount'],
                currency=parsed_data.get('currency', 'Taka'),
                category=parsed_data['category'],
                subcategory=parsed_data.get('subcategory'),
                merchant=parsed_data.get('merchant'),
                description=parsed_data.get('description'),
                date=datetime.fromisoformat(parsed_data['date']),
                payment_method=parsed_data.get('payment_method'),
                tags=parsed_data.get('tags', [])
            )
            
            # Create the expense
            result = ExpenseService.create_expense(db, user, expense_create)
            
            # Update with receipt URL if available
            if receipt_url and result['success']:
                expense = repo.get_expense_for_user(result['data'].id, user.id)
                if expense:
                    updated_expense = repo.set_receipt_url(expense, receipt_url)
                    result['data'] = ExpenseOut.model_validate(updated_expense)
            
            return {
                "success": True,
                "data": result['data'],
                "parsed_data": parsed_data,
                "confidence": parsed_data.get('confidence', 0.8),
                "message": "Expense created successfully from receipt"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "parsed_data": None,
                "confidence": 0,
                "message": f"Error parsing receipt: {str(e)}"
            }
    
    @staticmethod
    async def parse_voice_with_ai(db: Session, user: User, audio_file: UploadFile) -> dict:
        """Parse expense from voice recording using AI"""
        from app.services.ai_service import ai_service
        
        try:
            # Parse with AI
            parsed_data = await ai_service.parse_voice_expense(audio_file)
            
            if parsed_data.get('confidence', 0) < 0.5:
                return {
                    "success": False,
                    "data": None,
                    "parsed_data": parsed_data,
                    "confidence": parsed_data.get('confidence', 0),
                    "transcribed_text": parsed_data.get('transcribed_text'),
                    "message": "Low confidence in voice parsing. Please speak more clearly."
                }
            
            # Create expense from parsed data
            expense_create = ExpenseCreate(
                amount=parsed_data['amount'],
                currency=parsed_data.get('currency', 'Taka'),
                category=parsed_data['category'],
                subcategory=parsed_data.get('subcategory'),
                merchant=parsed_data.get('merchant'),
                description=parsed_data.get('description'),
                date=datetime.fromisoformat(parsed_data['date']),
                payment_method=parsed_data.get('payment_method'),
                tags=parsed_data.get('tags', [])
            )
            
            # Create the expense
            result = ExpenseService.create_expense(db, user, expense_create)
            
            return {
                "success": True,
                "data": result['data'],
                "parsed_data": parsed_data,
                "confidence": parsed_data.get('confidence', 0.8),
                "transcribed_text": parsed_data.get('transcribed_text'),
                "message": "Expense created successfully from voice"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "parsed_data": None,
                "confidence": 0,
                "transcribed_text": None,
                "message": f"Error parsing voice: {str(e)}"
            }
    
    @staticmethod
    async def get_ai_insights(db: Session, user: User, days: int = 30) -> dict:
        """Get AI-powered spending insights"""
        from app.services.ai_service import ai_service
        repo = ExpenseRepository(db)

        try:
            # Get recent expenses
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            expenses = repo.list_in_period(
                user.id,
                start_date=start_date,
                end_date=end_date,
            )
            
            if not expenses:
                return {
                    "success": True,
                    "data": {"insights": "No recent expenses found for analysis."},
                    "message": "No data available for insights"
                }
            
            # Convert expenses to dict format for AI
            expenses_data = []
            for expense in expenses:
                expenses_data.append({
                    "amount": expense.amount,
                    "currency": expense.currency,
                    "category": expense.category,
                    "merchant": expense.merchant,
                    "description": expense.description,
                    "date": expense.date.isoformat(),
                    "payment_method": expense.payment_method
                })
            
            # Get AI insights
            insights = await ai_service.get_spending_insights(expenses_data)
            
            return {
                "success": True,
                "data": insights,
                "message": "AI insights generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": {"insights": f"Error generating insights: {str(e)}"},
                "message": f"Error generating insights: {str(e)}"
            }
    
# ------------------------------------ Dashboard Analytics Methods ------------------------------------
    @staticmethod
    def get_total_spend_dashboard(db: Session, user: User) -> dict:
        """Get total spend data for dashboard - current month vs previous month"""
        repo = ExpenseRepository(db)
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get last day of current month
        _, last_day = calendar.monthrange(now.year, now.month)
        current_month_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        
        # Previous month calculation
        if now.month == 1:
            prev_year = now.year - 1
            prev_month = 12
        else:
            prev_year = now.year
            prev_month = now.month - 1
            
        previous_month_start = datetime(prev_year, prev_month, 1, 0, 0, 0, 0)
        _, prev_last_day = calendar.monthrange(prev_year, prev_month)
        previous_month_end = datetime(prev_year, prev_month, prev_last_day, 23, 59, 59, 999999)
        
        # Get current month expenses
        current_month_expenses = repo.sum_in_period(
            user.id,
            start_date=current_month_start,
            end_date=current_month_end,
        )
        
        # Get previous month expenses
        previous_month_expenses = repo.sum_in_period(
            user.id,
            start_date=previous_month_start,
            end_date=previous_month_end,
        )
        
        # Calculate percentage change
        if previous_month_expenses > 0:
            percentage_change = ((current_month_expenses - previous_month_expenses) / previous_month_expenses) * 100
        else:
            percentage_change = 100 if current_month_expenses > 0 else 0
        
        # Determine change direction
        if percentage_change > 0:
            change_direction = "increase"
        elif percentage_change < 0:
            change_direction = "decrease"
        else:
            change_direction = "same"
        
        data = TotalSpendData(
            current_month=round(current_month_expenses, 2),
            previous_month=round(previous_month_expenses, 2),
            percentage_change=round(percentage_change, 2),
            change_direction=change_direction
        )
        
        return {
            "success": True,
            "data": data,
            "message": "Total spend data retrieved successfully"
        }
    
    @staticmethod
    def get_category_breakdown_dashboard(db: Session, user: User, period: str = "current_month") -> dict:
        """Get category breakdown for dashboard pie chart"""
        repo = ExpenseRepository(db)
        now = datetime.now()
        
        if period == "current_month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            _, last_day = calendar.monthrange(now.year, now.month)
            end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        elif period == "last_30_days":
            end_date = now
            start_date = now - timedelta(days=30)
        elif period == "current_year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        else:
            # Default to current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            _, last_day = calendar.monthrange(now.year, now.month)
            end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        
        categories = repo.get_category_totals_in_period(
            user.id,
            start_date=start_date,
            end_date=end_date,
        )
        
        if not categories:
            return {
                "success": True,
                "data": [],
                "message": "No expenses found for the selected period"
            }
        
        # Calculate total amount for percentage calculation
        total_amount = sum(float(cat.total_amount) for cat in categories)
        
        breakdown_data = []
        for cat in categories:
            amount_value = float(cat.total_amount)
            breakdown_data.append(CategoryBreakdownItem(
                category=cat.category,
                amount=round(amount_value, 2),
                percentage=round((amount_value / total_amount) * 100, 2) if total_amount > 0 else 0,
                transaction_count=cat.count
            ))
        
        # Sort by amount descending
        breakdown_data.sort(key=lambda x: x.amount, reverse=True)
        
        return {
            "success": True,
            "data": breakdown_data,
            "message": f"Category breakdown for {period} retrieved successfully"
        }
    
    @staticmethod
    def get_category_trend_dashboard(db: Session, user: User, months: int = 6) -> dict:
        """Get category trend data for dashboard - showing how each category evolves over time"""
        repo = ExpenseRepository(db)
        now = datetime.now()
        end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate start date by going back the specified number of months
        start_year = now.year
        start_month = now.month - months
        
        while start_month <= 0:
            start_month += 12
            start_year -= 1
            
        start_date = datetime(start_year, start_month, 1, 0, 0, 0, 0)
        
        monthly_data = repo.get_monthly_category_totals(
            user.id,
            start_date=start_date,
            end_date=end_date,
        )
        
        if not monthly_data:
            return {
                "success": True,
                "data": [],
                "message": "No expense data found for the specified period"
            }
        
        # Group by month to calculate percentages
        months_totals = {}
        month_categories = {}
        
        for item in monthly_data:
            month_key = f"{int(item.year)}-{int(item.month):02d}"
            if month_key not in months_totals:
                months_totals[month_key] = 0
                month_categories[month_key] = {}
            
            total_value = float(item.total_amount)
            months_totals[month_key] += total_value
            month_categories[month_key][item.category] = total_value
        
        trend_data = []
        
        for month_key, categories in month_categories.items():
            month_total = months_totals[month_key]
            for category, amount in categories.items():
                trend_data.append(CategoryTrendMonth(
                    month=month_key,
                    category=category,
                    amount=round(amount, 2),
                    percentage=round((amount / month_total) * 100, 2) if month_total > 0 else 0
                ))
        
        # Sort by month and then by amount
        trend_data.sort(key=lambda x: (x.month, -x.amount))
        
        return {
            "success": True,
            "data": trend_data,
            "message": f"Category trend data for last {months} months retrieved successfully"
        }
    
    @staticmethod
    def get_spend_trend_dashboard(db: Session, user: User, period: str = "daily", days: int = 30) -> dict:
        """Get spend trend data for dashboard line chart"""
        repo = ExpenseRepository(db)
        now = datetime.now()

        if period == "daily":
            start_date = now - timedelta(days=days)

            def bucket_info(expense_datetime: datetime):
                bucket = expense_datetime.date()
                return bucket, bucket.strftime("%Y-%m-%d")

        elif period == "weekly":
            weeks_back = max(days // 7, 4)
            start_date = now - timedelta(weeks=weeks_back)

            def bucket_info(expense_datetime: datetime):
                iso_year, iso_week, _ = expense_datetime.isocalendar()
                bucket = datetime.fromisocalendar(iso_year, iso_week, 1).date()
                return bucket, f"{iso_year}-W{iso_week:02d}"

        elif period == "monthly":
            months_back = max(days // 30, 3)
            start_date = now - timedelta(days=months_back * 30)

            def bucket_info(expense_datetime: datetime):
                month_start = expense_datetime.replace(day=1).date()
                return month_start, expense_datetime.strftime("%Y-%m")

        else:
            start_date = now - timedelta(days=30)

            def bucket_info(expense_datetime: datetime):
                bucket = expense_datetime.date()
                return bucket, bucket.strftime("%Y-%m-%d")

        expenses = repo.get_expenses_since(user.id, start_date)

        bucket_totals = defaultdict(lambda: {"amount": 0.0, "count": 0, "label": ""})
        for expense in expenses:
            if expense.date < start_date:
                continue
            bucket_key, label = bucket_info(expense.date)
            data = bucket_totals[bucket_key]
            data["amount"] += float(expense.amount)
            data["count"] += 1
            data["label"] = label

        trend_list = []
        for bucket_key in sorted(bucket_totals.keys()):
            bucket = bucket_totals[bucket_key]
            trend_list.append(
                SpendTrendData(
                    date=bucket["label"],
                    amount=round(bucket["amount"], 2),
                    transaction_count=bucket["count"],
                )
            )

        return {
            "success": True,
            "data": trend_list,
            "message": f"Spend trend data ({period}) retrieved successfully"
        }
    
    @staticmethod
    def get_top_transactions_dashboard(db: Session, user: User, period: str = "monthly", limit: int = 5) -> dict:
        """Get top transactions for dashboard"""
        repo = ExpenseRepository(db)
        now = datetime.now()
        
        if period == "weekly":
            start_date = now - timedelta(weeks=1)
        elif period == "monthly":
            # Go back one month
            if now.month == 1:
                prev_year = now.year - 1
                prev_month = 12
            else:
                prev_year = now.year
                prev_month = now.month - 1
            start_date = datetime(prev_year, prev_month, now.day, 0, 0, 0, 0)
        elif period == "yearly":
            start_date = datetime(now.year - 1, now.month, now.day, 0, 0, 0, 0)
        else:
            # Default to monthly
            if now.month == 1:
                prev_year = now.year - 1
                prev_month = 12
            else:
                prev_year = now.year
                prev_month = now.month - 1
            start_date = datetime(prev_year, prev_month, now.day, 0, 0, 0, 0)
        
        # Get top transactions by amount
        transactions = repo.get_top_transactions(
            user.id,
            start_date=start_date,
            limit=limit,
        )
        
        transaction_list = []
        
        for transaction in transactions:
            transaction_list.append(TopTransactionData(
                id=transaction.id,
                amount=round(transaction.amount, 2),
                category=transaction.category,
                merchant=transaction.merchant,
                description=transaction.description,
                date=transaction.date
            ))
        
        return {
            "success": True,
            "data": transaction_list,
            "message": f"Top {limit} transactions ({period}) retrieved successfully"
        }
