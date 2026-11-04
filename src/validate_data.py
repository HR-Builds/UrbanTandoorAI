
from pathlib import Path
import pandas as pd
import json

DATA = Path("data")
REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

MENU_FILE = DATA / "Urban_Tandoor_Complete_Menu_Catalog.xlsx"
INVENTORY_FILE = DATA / "Urban_Tandoor_Two_Branch_Inventory_Dataset.xlsx"

errors = []
warnings = []

def check_duplicate(df, column, sheet):
    if column not in df.columns:
        errors.append(f"{sheet}: Missing column {column}")
        return

    duplicates = df[df[column].duplicated(keep=False)]
    if not duplicates.empty:
        errors.append(
            f"{sheet}: {len(duplicates)} rows have duplicate {column}"
        )

def check_missing(df, columns, sheet):
    for column in columns:
        if column not in df.columns:
            errors.append(f"{sheet}: Missing column {column}")
            continue

        count = int(df[column].isna().sum())
        if count:
            warnings.append(
                f"{sheet}: {count} missing values in {column}"
            )

def main():
    menu = pd.read_excel(MENU_FILE, sheet_name=None)
    inventory = pd.read_excel(INVENTORY_FILE, sheet_name=None)

    print("Starting data validation...")

    # Menu validation
    items = menu["Menu_Items"]
    check_duplicate(items, "Menu_ID", "Menu_Items")
    check_missing(
        items,
        ["Menu_ID", "Item_Name", "Category", "Base_Price_PKR"],
        "Menu_Items"
    )

    if (pd.to_numeric(items["Base_Price_PKR"], errors="coerce") < 0).any():
        errors.append("Menu_Items: Negative base prices found")

    # Variant validation
    variants = menu["Variants"]
    check_duplicate(variants, "Variant_ID", "Variants")
    check_missing(
        variants,
        ["Variant_ID", "Menu_ID", "Variant_Name", "Price_PKR"],
        "Variants"
    )

    known_menu_ids = set(items["Menu_ID"].dropna().astype(str))
    variant_menu_ids = set(variants["Menu_ID"].dropna().astype(str))

    broken_variants = variant_menu_ids - known_menu_ids
    if broken_variants:
        errors.append(
            f"Variants: {len(broken_variants)} unknown Menu_ID references"
        )

    # Branch validation
    branches = inventory["Branches"]
    check_duplicate(branches, "Branch_ID", "Branches")

    stock = inventory["Branch_Stock"]
    check_missing(
        stock,
        ["Branch_ID", "Ingredient_ID", "On_Hand", "Reserved"],
        "Branch_Stock"
    )

    known_branch_ids = set(branches["Branch_ID"].dropna().astype(str))
    stock_branch_ids = set(stock["Branch_ID"].dropna().astype(str))

    if stock_branch_ids - known_branch_ids:
        errors.append("Branch_Stock: Unknown Branch_ID references found")

    ingredients = inventory["Ingredients"]
    check_duplicate(ingredients, "Ingredient_ID", "Ingredients")

    known_ingredients = set(
        ingredients["Ingredient_ID"].dropna().astype(str)
    )
    stock_ingredients = set(
        stock["Ingredient_ID"].dropna().astype(str)
    )

    if stock_ingredients - known_ingredients:
        errors.append("Branch_Stock: Unknown Ingredient_ID references found")

    # Recipe validation
    recipes = inventory["Recipes"]
    check_missing(
        recipes,
        ["Menu_ID", "Ingredient_ID", "Qty_Per_Portion"],
        "Recipes"
    )

    recipe_menu_ids = set(recipes["Menu_ID"].dropna().astype(str))
    unknown_recipes = recipe_menu_ids - known_menu_ids

    if unknown_recipes:
        errors.append(
            f"Recipes: {len(unknown_recipes)} unknown Menu_ID references"
        )

    recipe_ingredients = set(
        recipes["Ingredient_ID"].dropna().astype(str)
    )

    if recipe_ingredients - known_ingredients:
        errors.append("Recipes: Unknown Ingredient_ID references found")

    quantities = pd.to_numeric(
        recipes["Qty_Per_Portion"], errors="coerce"
    )

    if (quantities < 0).any():
        errors.append("Recipes: Negative ingredient quantities found")

    if quantities.isna().any():
        warnings.append("Recipes: Invalid or missing ingredient quantities")

    # Branch menu references
    branch_menu = menu["Branch_Menu"]

    if branch_menu["Menu_ID"].astype(str).isin(known_menu_ids).eq(False).any():
        errors.append("Branch_Menu: Unknown Menu_ID references found")

    print("\nValidation finished.")
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))

    report = {
        "errors": errors,
        "warnings": warnings,
        "status": "PASS" if not errors else "FAIL"
    }

    output = REPORTS / "validation_report.json"
    output.write_text(json.dumps(report, indent=4), encoding="utf-8")

    for issue in errors:
        print("ERROR:", issue)

    for issue in warnings:
        print("WARNING:", issue)

    print("\nReport saved:", output)

if __name__ == "__main__":
    main()
