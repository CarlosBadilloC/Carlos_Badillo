from odoo import models, api


class AIQueryHandler(models.AbstractModel):
    """
    AI Query Handler

    This model exposes EXPLICIT, NON-AMBIGUOUS methods
    intended to be called by AI Agents or orchestration layers.

    Scope:
    - Inventory (stockable products only)
    - CRM (opportunities only)

    Each method:
    - Has a single responsibility
    - Uses explicit domain definitions
    - Returns a predictable and uniform structure
    """

    _name = "ai.query.handler"
    _description = "AI Query Handler - Inventory and CRM (Unambiguous)"

    # ==========================================================
    # INVENTORY
    # ==========================================================

    @api.model
    def inventory_stock_summary(self):
        """
        PURPOSE:
        Returns a GLOBAL inventory summary for stockable products.

        DEFINITION:
        - Product type: stockable products only
        - Quantity source: qty_available (real stock)

        USE WHEN:
        - User asks for general inventory status
        - User asks how much stock exists in total

        RETURNS:
        - total_products: int
        - total_stock_quantity: float
        - low_stock_products: list (max 10)
        """

        try:
            Product = self.env["product.product"]

            domain = [
                ("type", "=", "product"),
                ("active", "=", True),
            ]

            products = Product.search(domain)

            total_stock_quantity = sum(
                p.qty_available for p in products
            )

            low_stock_products = [
                {
                    "product_id": p.id,
                    "product_name": p.display_name,
                    "qty_available": p.qty_available,
                    "uom": p.uom_id.name,
                }
                for p in products
                if 0 < p.qty_available <= 5
            ]

            return {
                "status": "success",
                "model": "product.product",
                "domain": domain,
                "total_products": len(products),
                "total_stock_quantity": total_stock_quantity,
                "low_stock_products": low_stock_products[:10],
            }

        except Exception as e:
            return self._error_response(e)

    @api.model
    def inventory_product_count(self):
        """
        PURPOSE:
        Returns ONLY the number of active stockable products.

        USE WHEN:
        - User asks: "How many products do we have?"
        - Count is needed, not stock quantity
        """

        try:
            domain = [
                ("type", "=", "product"),
                ("active", "=", True),
            ]

            count = self.env["product.product"].search_count(domain)

            return {
                "status": "success",
                "model": "product.product",
                "domain": domain,
                "total_products": count,
            }

        except Exception as e:
            return self._error_response(e)

    # ==========================================================
    # CRM
    # ==========================================================

    @api.model
    def crm_opportunity_global_summary(self):
        """
        PURPOSE:
        Returns a FULL CRM opportunity summary.

        DEFINITIONS:
        - Opportunity: crm.lead with type = 'opportunity'
        - Open: active AND probability between 1 and 99
        - Won: probability = 100
        - Lost: probability = 0 AND inactive

        USE WHEN:
        - User asks for CRM overview
        """

        try:
            Lead = self.env["crm.lead"]

            base_domain = [("type", "=", "opportunity")]

            open_domain = base_domain + [
                ("active", "=", True),
                ("probability", ">", 0),
                ("probability", "<", 100),
            ]

            won_domain = base_domain + [
                ("probability", "=", 100),
            ]

            lost_domain = base_domain + [
                ("probability", "=", 0),
                ("active", "=", False),
            ]

            open_leads = Lead.search(open_domain)

            total_expected_revenue = sum(
                lead.expected_revenue or 0 for lead in open_leads
            )

            return {
                "status": "success",
                "model": "crm.lead",
                "currency": self.env.company.currency_id.name,
                "domains": {
                    "open": open_domain,
                    "won": won_domain,
                    "lost": lost_domain,
                },
                "total_opportunities": Lead.search_count(base_domain),
                "open_opportunities": len(open_leads),
                "won_opportunities": Lead.search_count(won_domain),
                "lost_opportunities": Lead.search_count(lost_domain),
                "total_expected_revenue": total_expected_revenue,
            }

        except Exception as e:
            return self._error_response(e)

    @api.model
    def crm_open_opportunity_count(self):
        """
        PURPOSE:
        Returns ONLY the number of OPEN opportunities.

        USE WHEN:
        - User asks specifically for open opportunities count
        """

        try:
            domain = [
                ("type", "=", "opportunity"),
                ("active", "=", True),
                ("probability", ">", 0),
                ("probability", "<", 100),
            ]

            count = self.env["crm.lead"].search_count(domain)

            return {
                "status": "success",
                "model": "crm.lead",
                "domain": domain,
                "open_opportunities": count,
            }

        except Exception as e:
            return self._error_response(e)

    @api.model
    def crm_opportunities_grouped_by_stage(self):
        """
        PURPOSE:
        Returns opportunities grouped by CRM stage.

        USE WHEN:
        - User asks about pipeline stages
        - Funnel / pipeline analysis
        """

        try:
            Stage = self.env["crm.stage"]
            Lead = self.env["crm.lead"]

            stages_data = []

            for stage in Stage.search([], order="sequence"):
                domain = [
                    ("type", "=", "opportunity"),
                    ("stage_id", "=", stage.id),
                    ("active", "=", True),
                ]

                opportunities = Lead.search(domain)

                if not opportunities:
                    continue

                stages_data.append({
                    "stage_id": stage.id,
                    "stage_name": stage.name,
                    "sequence": stage.sequence,
                    "opportunity_count": len(opportunities),
                    "expected_revenue": sum(
                        opp.expected_revenue or 0
                        for opp in opportunities
                    ),
                })

            return {
                "status": "success",
                "model": "crm.lead",
                "currency": self.env.company.currency_id.name,
                "stages": stages_data,
                "total_stages": len(stages_data),
            }

        except Exception as e:
            return self._error_response(e)

    # ==========================================================
    # COMMON
    # ==========================================================

    def _error_response(self, exception):
        """
        Unified error response for AI-safe consumption.
        """
        return {
            "status": "error",
            "error_type": exception.__class__.__name__,
            "message": str(exception),
        }
