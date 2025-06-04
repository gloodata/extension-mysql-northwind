from glootil import Toolbox, DynEnum
from enum import Enum
from state import State
import logging
from datetime import date

logger = logging.getLogger("toolbox")
NS = "gd-northwind"
tb = Toolbox(NS, "Northwind", "Northwind Explorer", state=State())


# =====================================
# Utilities to create charts and tables
# =====================================
def create_group_chart(title, cols, rows, unit="", chart_type="bar"):
    on_clicks = []
    col_keys = [col[0] for col in cols]
    row_lists = [[row.get(key) for key in col_keys] for row in rows]

    result = {
        "info": {
            "type": "group",
            "chartType": chart_type,
            "title": title,
            "unit": unit,
            "keyName": cols[0][0],
            "valName": cols[1][0],
            "onClick": on_clicks,
        },
        "data": {"cols": cols, "rows": row_lists},
    }
    return result


def create_series_chart(title, cols, rows, chart_type="bar"):
    x, x_title = cols[0]
    serie, serie_title = cols[1]
    y, y_title = cols[2]

    col_keys = [col[0] for col in cols]
    row_lists = [[row.get(key) for key in col_keys] for row in rows]
    on_clicks = []

    return {
        "type": "Series",
        "chartType": chart_type,
        "title": title,
        "unit": "#",
        "xColTitle": x_title,
        "yColTitle": y_title,
        "seriesCol": serie,
        "xCol": x,
        "valCols": [y],
        "pivot": {
            "keyName": serie,
            "valName": y,
        },
        "cols": cols,
        "rows": row_lists,
        "onClick": on_clicks,
    }


def to_area(rows):
    areas = [{"name": row[0], "value": row[1]} for idx, row in enumerate(rows)]
    return areas


def create_area_map(title, cols, rows, map_type="usa"):
    col_keys = [col[0] for col in cols]
    row_lists = [[row.get(key) for key in col_keys] for row in rows]
    areas = to_area(row_lists)
    on_clicks = []
    result = {
        "type": "AreaMap",
        "mapId": map_type,
        "infoId": map_type,
        "onClick": on_clicks,
        "items": areas,
    }
    return result


def create_table(columns, rows):
    on_clicks = []
    rows_values = [
        [
            row[col["id"]]
            for col in columns
        ]
        for row in rows
    ]
    return {
        "type": "Table",
        "columns": columns,
        "rows": rows_values,
        "onClick": on_clicks,
    }


# ================================
# Declaration of enums and filters
# ================================
@tb.enum(name="category", icon="list")
class Category(DynEnum):
    """
    Category of products, used for filtering and analysis.
    """

    @staticmethod
    async def search(state: State, query: str = "", limit: int = 100):
        return await state.search("category_enum", query, limit)

    @staticmethod
    async def find_best_match(state: State, query: str = ""):
        return await Category.search(state, query, limit=1)


@tb.enum(name="jobtitle", icon="list")
class JobTitle(DynEnum):
    """
    Job title of employees, used for filtering and analysis.
    """

    @staticmethod
    async def search(state: State, query: str = "", limit: int = 100):
        return await state.search("job_title_enum", query, limit)

    @staticmethod
    async def find_best_match(state: State, query: str = ""):
        return await JobTitle.search(state, query, limit=1)


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
    manual_update=False,
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
    - revenue kpi: The key performance indicator to analyze: total reveneu, order count, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - category: Optional category filter to focus on specific product category

    Result:
    - A bar chart showing total revenue, order count, or average order value by category
    """
    rows = await state.select_many(
        "revenue_by_category",
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI
    if kpi == KPI.TOTAL_ORDERS:
        chart = "pie"
    else:
        chart = "bar"

    return create_group_chart(
        "Revenue Analysis by product category",
        [["category", "Category"], [kpi.name.lower(), kpi.value]],
        rows,
        chart_type=chart
    )


# 2. Revenue by category by month
@tb.tool(
    name="Revenue analysis by category by month",
    examples=[
        "Total revenue by category by day",
        "Order count by product category by day",
        "Average order value by category by day",
    ],
    manual_update=False,
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
    - revenue kpi: The key performance indicator to analyze: total reveneu, order count, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - category: Optional category filter to focus on specific product category

    Result:
    - A bar chart showing total revenue, order count, or average order value by category by month
    """
    rows = await state.select_many(
        "revenue_by_category_by_month",
        start_date=start_date,
        end_date=end_date,
        category=category,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI

    return create_series_chart(
        "Revenue analysis by product category by month",
        [["date", "Date"], ["category", "Category"], [kpi.name.lower(), kpi.value]],
        rows,
        chart_type="line",
    )


# 3. Employee performance
@tb.tool(
    name="Employee performance analysis",
    examples=[
        "Total revenue by employee",
        "Order count by employee",
        "Unique customers by employee",
        "Average order value by employee",
    ],
    manual_update=False,
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
    - employee kpi: The key performance indicator to analyze: total reveneu, order count, unique customers, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - job_title: Optional job title filter to focus on specific employee roles

    Result:
    - A bar chart showing total revenue, order count, unique customers or average order value by employee
    """
    rows = await state.select_many(
        "employee_performance",
        start_date=start_date,
        end_date=end_date,
        job_title=job_title,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI

    return create_group_chart(
        "Performance analysis by employee",
        [["employee", "Employee"], [kpi.name.lower(), kpi.value]],
        rows,
        chart_type="bar",
    )


# 4. Employee performance by month
@tb.tool(
    name="Employee performance analysis by month",
    examples=[
        "Total revenue by employee by month",
        "Order count by employee by month",
        "Unique customers by employee by month",
        "Average order value by employee by month",
    ],
    manual_update=False,
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
    - employee kpi: The key performance indicator to analyze: total reveneu, order count, unique customers, avg order value (default is total_revenue)
    - start_date: start date filter. Mandatory, default is today minus 1 year
    - end_date: end date filter. Mandatory, default is today.
    - job_title: Optional job title filter to focus on specific employee roles

    Result:
    - A bar chart showing total revenue, order count, unique customers or average order value by employee by month
    """
    rows = await state.select_many(
        "employee_performance_by_month",
        start_date=start_date,
        end_date=end_date,
        job_title=job_title,
    )

    # The kpi.name is equal to the column name in the rows
    # and kpi.value is the label for the KPI

    return create_series_chart(
        "Performance analysis by employee by month",
        [["date", "Date"], ["employee", "Employee"], [kpi.name.lower(), kpi.value]],
        rows,
        chart_type="heatmap",
    )


# 5. Customer Geography Analysis
@tb.tool(
    name="Customer geography analysis",
    examples=["Customer by state", "Geographic analysis", "Regional performance"],
    manual_update=False,
)
async def customer_geography_analysis(state: State, kpi: KPI = KPI.TOTAL_REVENUE):
    """
    Analyzes customer distribution and purchasing behavior by geographic location.

    Result:
    - An areamap visualization showing customer concentration and revenue by region
    """
    rows = await state.select_many(
        "customer_geography_analysis",
    )
    return create_area_map(
        "Customer geographic distribution",
        [["state_province", "State"], [kpi.name.lower(), kpi.value]],
        rows,
        map_type="usa",
    )


# 6. Product Performance Analysis
@tb.tool(
    name="Product performance analysis",
    examples=["Product performance", "Best selling products", "Product profitability"],
    manual_update=False,
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
    - discontinued: Filter by discontinuation status (-1 for all, 0 for active, 1 for discontinued)

    Result:
    - A detailed table showing product metrics including profitability analysis
    """
    rows = await state.select_many(
        "product_performance",
        start_date=start_date,
        end_date=end_date,
        category=category,
    )
    return create_table([
        {"id": "product_name", "label": "Product", "visible": True},
        {"id": "category", "label": "Category", "visible": True},
        {"id": "list_price", "label": "List Price", "visible": False},
        {"id": "standard_cost", "label": "Cost", "visible": False},
        {"id": "profit_margin", "label": "Profit Margin", "visible": True},
        {"id": "total_quantity_sold", "label": "Units Sold", "visible": True},
        {"id": "total_revenue", "label": "Revenue", "visible": True},
        {"id": "order_frequency", "label": "Order Frequency", "visible": True},
        {"id": "discontinued", "label": "Discontinued", "visible": False}
    ], rows)
