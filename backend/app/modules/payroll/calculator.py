from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date
from .models import ComplianceSettings, ProfessionalTaxSlab

class PayrollCalculator:
    """
    Pure logic calculation engine for Indian payroll statutory compliance.
    Receives data and returns calculated amounts. No database calls.
    """

    def calculate(
        self,
        structure_components: List[Any],  # List of SalaryStructureComponent objects
        compliance: ComplianceSettings,
        working_days: int,
        present_days: float,
        lop_days: float,
        pt_slabs: List[ProfessionalTaxSlab],
        is_february: bool,
        estimated_annual_tax: float = 0,
        lop_component_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Calculate all payroll components and totals.
        Returns a dictionary matching SalarySlip model fields.
        """
        # Step 1: Pro-rata factor
        pro_rata = present_days / working_days if working_days > 0 else 0
        
        # Step 2: Calculate Basic
        # Find component with calculation_type="Percentage of Gross" or "Fixed"
        # We assume "Basic" is identified by its name or a specific property, but here 
        # we'll look for calculation_type="Fixed" or "Percentage of Gross" as per instructions.
        # Most ERPs have one "Fixed" component as Basic.
        basic = 0.0
        for sc in structure_components:
            # Check if component is "Basic" - commonly the first earning
            # The prompt says: "Find component with calculation_type='Percentage of Gross' or 'Fixed'"
            # If several are fixed, we sum them? Usually Basic is specifically "Fixed".
            # For this MVP, we'll assume the primary "Fixed" earning is Basic.
            if sc.salary_component.component_name.lower() == "basic":
                if sc.calculation_type == "Fixed":
                    basic = float(sc.value) * pro_rata
                break
        
        # Step 3: Calculate all Earnings in order_index sequence
        earnings_list = []
        gross_earnings = 0.0
        
        # Sort by order_index
        sorted_components = sorted(structure_components, key=lambda x: x.order_index)
        
        # Calculate non-Percentage of Gross earnings first
        for sc in sorted_components:
            comp = sc.salary_component
            if comp.component_type == "Earning":
                amount = 0.0
                if sc.calculation_type == "Fixed":
                    amount = float(sc.value) * pro_rata
                elif sc.calculation_type == "Percentage of Basic":
                    amount = (float(sc.value) / 100) * basic # basic is already pro-rated
                elif sc.calculation_type == "Percentage of Gross":
                    continue # Calculate later
                
                earnings_list.append({
                    "salary_component_id": comp.id,
                    "component_name": comp.component_name,
                    "amount": round(amount, 2)
                })
                gross_earnings += round(amount, 2)
                
        # Calculate Percentage of Gross earnings (Iterative/Calculated after fixed)
        # For simplicity in this logic: Gross = Fixed_Earnings / (1 - Sum_of_Gross_Percentages)
        # But let's follow the prompt's instruction: "calculate after all fixed earnings are summed"
        gross_percentage_sum = sum(float(sc.value) / 100 for sc in sorted_components 
                                  if sc.salary_component.component_type == "Earning" 
                                  and sc.calculation_type == "Percentage of Gross")
        
        if gross_percentage_sum < 1:
            # Total Gross = Fixed Earnings / (1 - Gross %)
            current_fixed_gross = gross_earnings
            total_gross = current_fixed_gross / (1 - gross_percentage_sum)
            
            for sc in sorted_components:
                comp = sc.salary_component
                if comp.component_type == "Earning" and sc.calculation_type == "Percentage of Gross":
                    amount = (float(sc.value) / 100) * total_gross
                    earnings_list.append({
                        "salary_component_id": comp.id,
                        "component_name": comp.component_name,
                        "amount": round(amount, 2)
                    })
                    gross_earnings += round(amount, 2)
        
        # Step 4: LOP Deduction
        lop_deduction_amount = 0.0
        if working_days > 0:
            lop_deduction_amount = round((basic / pro_rata / working_days) * lop_days, 2) if pro_rata > 0 else 0.0
        
        deductions_list = []
        if lop_deduction_amount > 0 and lop_component_id:
            deductions_list.append({
                "salary_component_id": lop_component_id,
                "component_name": "LOP Deduction",
                "amount": lop_deduction_amount
            })

        # Step 5: PF Calculation
        pf_employee = 0.0
        pf_employer = 0.0
        eps_employer = 0.0
        if compliance.pf_applicable:
            pf_wage = min(basic, float(compliance.pf_wage_ceiling))
            pf_employee = round(pf_wage * 0.12, 2)
            pf_employer = round(pf_wage * 0.12, 2)
            # EPS is 8.33% of wage (capped at 15000), remainder goes to EPF
            eps_wage = min(pf_wage, 15000.0)
            eps_employer = round(eps_wage * 0.0833, 2)
            
            deductions_list.append({
                "component_name": "Provident Fund - Employee",
                "amount": pf_employee,
                "is_statutory": True
            })

        # Step 6: ESI Calculation
        esi_employee = 0.0
        esi_employer = 0.0
        if compliance.esi_applicable:
            if gross_earnings <= float(compliance.esi_gross_ceiling):
                esi_employee = round(gross_earnings * 0.0075, 2)
                esi_employer = round(gross_earnings * 0.0325, 2)
                
                deductions_list.append({
                    "component_name": "ESI - Employee",
                    "amount": esi_employee,
                    "is_statutory": True
                })

        # Step 7: PT Calculation
        professional_tax = 0.0
        if compliance.pt_applicable:
            for slab in pt_slabs:
                if slab.is_february != is_february:
                    continue
                
                min_sal = float(slab.min_salary)
                max_sal = float(slab.max_salary) if slab.max_salary is not None else float('inf')
                
                if gross_earnings >= min_sal and gross_earnings <= max_sal:
                    professional_tax = float(slab.pt_amount)
                    break
            
            if professional_tax > 0:
                deductions_list.append({
                    "component_name": "Professional Tax",
                    "amount": professional_tax,
                    "is_statutory": True
                })

        # Step 8: TDS Calculation
        tds_amount = 0.0
        if compliance.tds_applicable:
            tds_amount = round(estimated_annual_tax / 12, 2)
            if tds_amount > 0:
                deductions_list.append({
                    "component_name": "TDS",
                    "amount": tds_amount,
                    "is_statutory": True
                })

        # Step 9: Totals
        total_deductions = round(pf_employee + esi_employee + professional_tax + tds_amount + lop_deduction_amount, 2)
        net_pay = round(gross_earnings - total_deductions, 2)

        return {
            "gross_earnings": gross_earnings,
            "pf_employee": pf_employee,
            "pf_employer": pf_employer,
            "eps_employer": eps_employer,
            "esi_employee": esi_employee,
            "esi_employer": esi_employer,
            "professional_tax": professional_tax,
            "tds_amount": tds_amount,
            "lop_days": lop_days,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "earnings": earnings_list,
            "deductions": deductions_list
        }
