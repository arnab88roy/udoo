from decimal import Decimal
from typing import List, Optional, Literal

class GSTCalculator:
    """
    Determines GST type and calculates tax amounts.
    Used for Indian companies invoicing Indian clients.
    For non-Indian transactions, falls back to TaxTemplate.
    """

    @staticmethod
    def determine_gst_type(
        company_state_code: Optional[str],
        client_state_code: Optional[str],
        client_country_code: str = "IN"
    ) -> Literal["cgst_sgst", "igst", "export", "none"]:
        """
        Rules:
        - If client is not Indian → "export" (zero-rated)
        - If both state codes present and equal → "cgst_sgst"
        - If both state codes present but different → "igst"
        - If either state code missing → "none" (cannot determine)
        """
        if client_country_code != "IN":
            return "export"
        if not company_state_code or not client_state_code:
            return "none"
        if company_state_code == client_state_code:
            return "cgst_sgst"
        return "igst"

    @staticmethod
    def calculate_line_tax(
        taxable_amount: Decimal,
        tax_template_lines: List[dict],
        gst_type: str,
    ) -> dict:
        """
        Calculates tax breakdown for one line item.

        For cgst_sgst: splits total rate into CGST + SGST (equal halves)
        For igst: applies full rate as IGST
        For export/none: zero tax

        Returns:
            {
                "cgst": Decimal,
                "sgst": Decimal,
                "igst": Decimal,
                "other_taxes": List[dict],
                "total_tax": Decimal
            }
        """
        result = {
            "cgst": Decimal("0"),
            "sgst": Decimal("0"),
            "igst": Decimal("0"),
            "other_taxes": [],
            "total_tax": Decimal("0")
        }

        if gst_type in ("export", "none"):
            return result

        for line in tax_template_lines:
            rate = Decimal(str(line["rate"])) / 100
            tax_amount = (taxable_amount * rate).quantize(Decimal("0.01"))

            tax_name = line["tax_name"].upper()

            if gst_type == "cgst_sgst":
                if tax_name in ("CGST", "SGST"):
                    if tax_name == "CGST":
                        result["cgst"] += tax_amount
                    else:
                        result["sgst"] += tax_amount
                    result["total_tax"] += tax_amount
                elif tax_name == "IGST":
                    # Split IGST into CGST+SGST for intra-state
                    half = (tax_amount / 2).quantize(Decimal("0.01"))
                    result["cgst"] += half
                    result["sgst"] += tax_amount - half
                    result["total_tax"] += tax_amount
                else:
                    result["other_taxes"].append({
                        "name": tax_name,
                        "amount": float(tax_amount)
                    })
                    result["total_tax"] += tax_amount

            elif gst_type == "igst":
                if tax_name in ("IGST", "CGST", "SGST"):
                    # For inter-state, use IGST at combined rate
                    result["igst"] += tax_amount
                    result["total_tax"] += tax_amount
                else:
                    result["other_taxes"].append({
                        "name": tax_name,
                        "amount": float(tax_amount)
                    })
                    result["total_tax"] += tax_amount

        return result
