import pytest
from app.modules.payroll.calculator import PayrollCalculator
from app.modules.payroll.models import ComplianceSettings, ProfessionalTaxSlab, SalaryComponent, SalaryStructureComponent
from uuid import uuid4

@pytest.fixture
def calculator():
    return PayrollCalculator()

@pytest.fixture
def compliance():
    return ComplianceSettings(
        pf_applicable=True,
        esi_applicable=True,
        pt_applicable=True,
        tds_applicable=True,
        pf_wage_ceiling=15000,
        esi_gross_ceiling=21000
    )

@pytest.fixture
def pt_slabs():
    return [
        ProfessionalTaxSlab(state_code="MH", min_salary=0, max_salary=7500, pt_amount=0, is_february=False),
        ProfessionalTaxSlab(state_code="MH", min_salary=7501, max_salary=10000, pt_amount=175, is_february=False),
        ProfessionalTaxSlab(state_code="MH", min_salary=10001, max_salary=999999, pt_amount=200, is_february=False),
        ProfessionalTaxSlab(state_code="MH", min_salary=10001, max_salary=999999, pt_amount=300, is_february=True)
    ]

@pytest.fixture
def basic_salary_structure():
    # Helper to create structure components
    basic = SalaryComponent(id=uuid4(), component_name="Basic", component_type="Earning")
    hra = SalaryComponent(id=uuid4(), component_name="HRA", component_type="Earning")
    
    sc1 = SalaryStructureComponent(salary_component=basic, value=20000, calculation_type="Fixed", order_index=1)
    sc2 = SalaryStructureComponent(salary_component=hra, value=50, calculation_type="Percentage of Basic", order_index=2)
    
    return [sc1, sc2]

def test_full_month_calculation(calculator, compliance, pt_slabs, basic_salary_structure):
    # Working 30, Present 30 (Full month)
    res = calculator.calculate(
        structure_components=basic_salary_structure,
        compliance=compliance,
        working_days=30,
        present_days=30,
        lop_days=0,
        pt_slabs=pt_slabs,
        is_february=False,
        estimated_annual_tax=12000 # 1000 per month
    )
    
    assert res["gross_earnings"] == 30000.0 # (20000 Basic + 10000 HRA)
    assert res["pf_employee"] == 1800.0 # (12% of 15000 ceiling)
    assert res["esi_employee"] == 0 # (Gross 30000 > 21000 ceiling)
    assert res["professional_tax"] == 200.0
    assert res["tds_amount"] == 1000.0
    assert res["net_pay"] == 30000.0 - (1800 + 200 + 1000) # 27000.0

def test_pro_rata_calculation(calculator, compliance, pt_slabs, basic_salary_structure):
    # Working 30, Present 15 (Half month)
    res = calculator.calculate(
        structure_components=basic_salary_structure,
        compliance=compliance,
        working_days=30,
        present_days=15,
        lop_days=0,
        pt_slabs=pt_slabs,
        is_february=False
    )
    
    # Basic = 20000 * (15/30) = 10000
    # HRA = 50% of 10000 = 5000
    assert res["gross_earnings"] == 15000.0
    assert res["pf_employee"] == 1200.0 # (12% of 10000)
    assert res["esi_employee"] == 15000 * 0.0075 # 112.5
    assert res["professional_tax"] == 200.0 # (Gross 15000 is still in top slab)

def test_february_pt_calculation(calculator, compliance, pt_slabs, basic_salary_structure):
    res = calculator.calculate(
        structure_components=basic_salary_structure,
        compliance=compliance,
        working_days=28,
        present_days=28,
        lop_days=0,
        pt_slabs=pt_slabs,
        is_february=True
    )
    assert res["professional_tax"] == 300.0

def test_calculator_pf_not_applicable(calculator, basic_salary_structure):
    compliance_no_pf = ComplianceSettings(
        pf_applicable=False,
        esi_applicable=False,
        pt_applicable=False,
        tds_applicable=False,
        pf_wage_ceiling=15000,
        esi_gross_ceiling=21000
    )
    res = calculator.calculate(
        structure_components=basic_salary_structure,
        compliance=compliance_no_pf,
        working_days=30,
        present_days=30,
        lop_days=0,
        pt_slabs=[],
        is_february=False
    )
    assert res["pf_employee"] == 0
    assert res["pf_employer"] == 0
    assert res["esi_employee"] == 0
    assert res["professional_tax"] == 0

def test_calculator_esi_above_ceiling(calculator, compliance, basic_salary_structure):
    # ESI should be zero when gross exceeds ceiling
    res = calculator.calculate(
        structure_components=basic_salary_structure,  # Basic=20000, HRA=10000 = Gross 30000
        compliance=compliance,  # esi_gross_ceiling=21000
        working_days=30,
        present_days=30,
        lop_days=0,
        pt_slabs=[],
        is_february=False
    )
    assert res["gross_earnings"] == 30000.0
    assert res["esi_employee"] == 0  # 30000 > 21000 ceiling
    assert res["esi_employer"] == 0

def test_calculator_pf_wage_ceiling(calculator, compliance, basic_salary_structure):
    # PF must be capped at pf_wage_ceiling even if basic is higher
    res = calculator.calculate(
        structure_components=basic_salary_structure,  # Basic=20000 (above 15000 ceiling)
        compliance=compliance,  # pf_wage_ceiling=15000
        working_days=30,
        present_days=30,
        lop_days=0,
        pt_slabs=[],
        is_february=False
    )
    # PF must be 12% of 15000 (ceiling), NOT 12% of 20000
    assert res["pf_employee"] == 1800.0  # 15000 * 0.12
    assert res["pf_employer"] == 1800.0
    assert res["eps_employer"] == round(15000 * 0.0833, 2)  # 1249.5

def test_lop_deduction(calculator, compliance, basic_salary_structure):
    res = calculator.calculate(
        structure_components=basic_salary_structure,  # Basic=20000
        compliance=compliance,
        working_days=26,
        present_days=24,
        lop_days=2,  # 2 days LOP
        pt_slabs=[],
        is_february=False
    )
    # LOP = (20000 / 26) * 2 = 1538.46
    expected_lop = round((20000 / 26) * 2, 2)
    assert res["net_pay"] == round(res["gross_earnings"] - res["total_deductions"], 2)
    # LOP must be included in total_deductions
    assert res["total_deductions"] >= expected_lop
