import logging
from datetime import date
from enum import Enum

from glootil import DynEnum, Toolbox

from state import State

logger = logging.getLogger("toolbox")
NS = "gd-northwind"
tb = Toolbox(NS, "Northwind", "Northwind Explorer", state=State())


# ================================
# Declaration of enums and filters
# ================================
@tb.enum(icon="list")
class Category(DynEnum):
    """
    Category of products, used for filtering and analysis.
    """

    @staticmethod
    async def search(state: State, query: str = "", limit: int = 100):
        return await state.search("category_enum", query, limit)


@tb.enum(icon="list")
class JobTitle(DynEnum):
    """
    Job title of employees, used for filtering and analysis.
    """

    @staticmethod
    async def search(state: State, query: str = "", limit: int = 100):
        return await state.search("job_title_enum", query, limit)


@tb.enum(icon="unit")
class KPI(Enum):
    """
    KPI (Key Performance Indicator) to select the analysis to show.
    """

    TOTAL_ORDERS = "Total orders"
    TOTAL_REVENUE = "Total revenue"
    UNIQUE_CUSTOMERS = "Unique customers"
    AVG_ORDER_VALUE = "Avg order value"


# ====================
# Declaration of tools
# ====================


# 1. Revenue by category
@tb.tool(
    name="Revenue analysis by category",
    examples=[
        "Total revenue by category",
        "Order count by product category",
        "Average order value by category",
    ],
    args={"start_date": "from", "end_date": "to"},
)
async def revenue_by_category(
    state: State,
    start_date: date,
    end_date: date,
    kpi: KPI = KPI.TOTAL_REVENUE,
    category: Category = None,
):
    """
    Analyzes revenue and order performance by product category with date and optional category filtering.

    Parameters:
    - revenue kpi: The key performance indicator to analyze: total revenue, order count, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - category: Optional category filter to focus on specific product category

    Result:
    - A bar chart showing total revenue, order count, or average order value by category
    """
    rows = await state.run_query(
        "revenue_by_category",
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI
    chart_type = "pie" if kpi == KPI.TOTAL_ORDERS else "bar"
    kpi_column = kpi.name.lower()

    # Convert rows to the expected format
    row_data = [[row["category"], row[kpi_column]] for row in rows]

    return {
        "info": {
            "type": "group",
            "chartType": chart_type,
            "title": "Revenue Analysis by product category",
            "unit": "",
            "keyName": "category",
            "valName": kpi_column,
        },
        "data": {
            "cols": [["category", "Category"], [kpi_column, kpi.value]],
            "rows": row_data,
        },
    }


# 2. Revenue by category by month
@tb.tool(
    name="Revenue analysis by category by month",
    examples=[
        "Total revenue by category by day",
        "Order count by product category by day",
        "Average order value by category by day",
    ],
    args={"start_date": "from", "end_date": "to"},
)
async def revenue_by_category_by_month(
    state: State,
    start_date: date,
    end_date: date,
    kpi: KPI = KPI.TOTAL_REVENUE,
    category: Category = None,
):
    """
    Analyzes revenue and order performance by product category by month with date and optional category filtering.

    Parameters:
    - revenue kpi: The key performance indicator to analyze: total revenue, order count, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - category: Optional category filter to focus on specific product category

    Result:
    - A line chart showing total revenue, order count, or average order value by category by month
    """
    rows = await state.run_query(
        "revenue_by_category_by_month",
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI
    kpi_column = kpi.name.lower()

    # Convert rows to the expected format
    row_data = [[row["date"], row["category"], row[kpi_column]]
                for row in rows]

    return {
        "type": "Series",
        "chartType": "line",
        "title": "Revenue analysis by product category by month",
        "unit": "#",
        "xColTitle": "Date",
        "yColTitle": kpi.value,
        "seriesCol": "category",
        "xCol": "date",
        "valCols": [kpi_column],
        "pivot": {
            "keyName": "category",
            "valName": kpi_column,
        },
        "cols": [["date", "Date"], ["category", "Category"], [kpi_column, kpi.value]],
        "rows": row_data,
    }


# 3. Employee performance
@tb.tool(
    name="Employee performance analysis",
    examples=[
        "Total revenue by employee",
        "Order count by employee",
        "Unique customers by employee",
        "Average order value by employee",
    ],
    args={"start_date": "from", "end_date": "to", "job_title": "job title"},
)
async def employee_performance(
    state: State,
    start_date: date,
    end_date: date,
    kpi: KPI = KPI.TOTAL_REVENUE,
    job_title: JobTitle = None,
):
    """
    Displays employee sales performance metrics including revenue, orders, and customer reach.

    Parameters:
    - employee kpi: The key performance indicator to analyze: total revenue, order count, unique customers, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - job_title: Optional job title filter to focus on specific employee roles

    Result:
    - A bar chart showing total revenue, order count, unique customers or average order value by employee
    """
    rows = await state.run_query(
        "employee_performance",
        start_date=start_date,
        end_date=end_date,
        job_title=job_title,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI
    kpi_column = kpi.name.lower()

    # Convert rows to the expected format
    row_data = [[row["employee"], row[kpi_column]] for row in rows]

    return {
        "info": {
            "type": "group",
            "chartType": "bar",
            "title": "Performance analysis by employee",
            "unit": "",
            "keyName": "employee",
            "valName": kpi_column,
        },
        "data": {
            "cols": [["employee", "Employee"], [kpi_column, kpi.value]],
            "rows": row_data,
        },
    }


# 4. Employee performance by month
@tb.tool(
    name="Employee performance analysis by month",
    examples=[
        "Total revenue by employee by month",
        "Order count by employee by month",
        "Unique customers by employee by month",
        "Average order value by employee by month",
    ],
    args={"start_date": "from", "end_date": "to", "job_title": "job title"},
)
async def employee_performance_by_month(
    state: State,
    start_date: date,
    end_date: date,
    kpi: KPI = KPI.TOTAL_REVENUE,
    job_title: JobTitle = None,
):
    """
    Displays employee sales performance metrics by month including revenue, orders, and customer reach.

    Parameters:
    - employee kpi: The key performance indicator to analyze: total revenue, order count, unique customers, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - job_title: Optional job title filter to focus on specific employee roles

    Result:
    - A heatmap showing total revenue, order count, unique customers or average order value by employee by month
    """
    rows = await state.run_query(
        "employee_performance_by_month",
        start_date=start_date,
        end_date=end_date,
        job_title=job_title,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI
    kpi_column = kpi.name.lower()

    # Convert rows to the expected format
    row_data = [[row["date"], row["employee"], row[kpi_column]]
                for row in rows]

    return {
        "type": "Series",
        "chartType": "heatmap",
        "title": "Performance analysis by employee by month",
        "unit": "#",
        "xColTitle": "Date",
        "yColTitle": kpi.value,
        "seriesCol": "employee",
        "xCol": "date",
        "valCols": [kpi_column],
        "pivot": {
            "keyName": "employee",
            "valName": kpi_column,
        },
        "cols": [["date", "Date"], ["employee", "Employee"], [kpi_column, kpi.value]],
        "rows": row_data,
    }


# 5. Customer Geography Analysis
@tb.tool(
    name="Customer geography analysis",
    examples=["Customer by state",
              "Geographic analysis", "Regional performance"],
)
async def customer_geography_analysis(state: State, kpi: KPI = KPI.TOTAL_REVENUE):
    """
    Analyzes customer distribution and purchasing behavior by geographic location.

    Result:
    - An area map visualization showing customer concentration and revenue by region
    """
    rows = await state.run_query("customer_geography_analysis")

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI
    kpi_column = kpi.name.lower()

    # Convert rows to the expected format
    items = [{"name": row["state_province"], "value": row[kpi_column]}
             for row in rows]

    return {
        "type": "AreaMap",
        "mapId": "usa",
        "items": items,
    }


# 6. Product Performance Analysis
@tb.tool(
    name="Product performance analysis",
    examples=["Product performance",
              "Best selling products", "Product profitability"],
    args={"start_date": "from", "end_date": "to"},
)
async def product_performance_analysis(
    state: State, start_date: date, end_date: date, category: Category = None
):
    """
    Comprehensive product analysis showing sales performance, profitability, and inventory status.

    Parameters:
    - start_date: start date filter (YYYY-MM-DD format)
    - end_date: end date filter (YYYY-MM-DD format)
    - category: Optional category filter

    Result:
    - A detailed table showing product metrics including profitability analysis
    """
    rows = await state.run_query(
        "product_performance",
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    # Convert rows to the expected format
    row_data = [
        [
            row["product_name"],
            row["category"],
            row["list_price"],
            row["standard_cost"],
            row["profit_margin"],
            row["total_quantity_sold"],
            row["total_revenue"],
            row["order_frequency"],
            row["discontinued"],
        ]
        for row in rows
    ]

    return {
        "type": "Table",
        "columns": [
            {"id": "product_name", "label": "Product", "visible": True},
            {"id": "category", "label": "Category", "visible": True},
            {"id": "list_price", "label": "List Price", "visible": False},
            {"id": "standard_cost", "label": "Cost", "visible": False},
            {"id": "profit_margin", "label": "Profit Margin", "visible": True},
            {"id": "total_quantity_sold", "label": "Units Sold", "visible": True},
            {"id": "total_revenue", "label": "Revenue", "visible": True},
            {"id": "order_frequency", "label": "Order Frequency", "visible": True},
            {"id": "discontinued", "label": "Discontinued", "visible": False},
        ],
        "rows": row_data,
    }
