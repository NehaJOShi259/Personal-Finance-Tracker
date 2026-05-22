import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_FILE = "finance_data.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Type", "Category", "Amount", "Description", "Date"])

st.title("Personal Finance Tracker Dashboard")

income_categories = ["Salary", "Bonus", "Investment", "Other"]
expense_categories = ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Rent", "Other"]

st.subheader("Add Transaction")

transaction_type = st.selectbox("Type", ["Income", "Expense"])

if transaction_type == "Income":
    category = st.selectbox("Category", income_categories)
else:
    category = st.selectbox("Category", expense_categories)

amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
description = st.text_input("Description")
date = st.date_input("Date")

income_words = ["salary", "bonus", "pay", "investment", "profit", "interest", "income"]
expense_words = ["food", "bill", "travel", "transport", "rent", "shopping", "grocery", "movie", "fun"]

def detect_mismatch(transaction_type, description):
    text = description.lower()

    if transaction_type == "Income":
        for word in expense_words:
            if word in text:
                return word

    elif transaction_type == "Expense":
        for word in income_words:
            if word in text:
                return word

    return None

if st.button("Add Transaction"):

    mismatch_word = detect_mismatch(transaction_type, description)

    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    remaining_balance = total_income - total_expense

    if amount <= 0:
        st.error("Amount must be greater than zero.")

    elif mismatch_word:
        st.error(f"The word '{mismatch_word}' does not match with {transaction_type}.")

    elif transaction_type == "Expense" and remaining_balance < amount:
        st.error("Insufficient balance.")

    else:
        new_entry = pd.DataFrame({
            "Type": [transaction_type],
            "Category": [category],
            "Amount": [amount],
            "Description": [description],
            "Date": [date]
        })

        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Transaction added successfully.")

st.subheader("Transaction History")

st.dataframe(df)

total_income = df[df["Type"] == "Income"]["Amount"].sum()
total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
balance = total_income - total_expense

st.markdown(f"### Total Income: ₹{total_income:.2f}")
st.markdown(f"### Total Expenses: ₹{total_expense:.2f}")
st.markdown(f"### Remaining Balance: ₹{balance:.2f}")

st.subheader("Delete or Clear Data")

delete_index = st.number_input(
    "Enter row number to delete",
    min_value=0,
    step=1,
    format="%d"
)

if st.button("Delete Entry"):

    if 0 <= delete_index < len(df):

        df = df.drop(delete_index).reset_index(drop=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Entry deleted.")

    else:
        st.error("Invalid row number.")

if st.button("Clear All Data"):

    df = pd.DataFrame(columns=["Type", "Category", "Amount", "Description", "Date"])
    df.to_csv(DATA_FILE, index=False)

    st.success("All data cleared.")

st.subheader("Expense Breakdown by Category")

if not df.empty:

    expense_df = df[df["Type"] == "Expense"]

    if not expense_df.empty:

        category_sum = expense_df.groupby("Category")["Amount"].sum()

        fig1, ax1 = plt.subplots()

        ax1.pie(
            category_sum,
            labels=category_sum.index,
            autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
            startangle=90
        )

        plt.title("Expense Distribution (%)")

        st.pyplot(fig1)

    else:
        st.info("No expense data available.")

else:
    st.info("No transactions yet.")

st.subheader("Income vs Expense Comparison")

if not df.empty:

    summary = df.groupby("Type")["Amount"].sum().reindex(
        ["Income", "Expense"],
        fill_value=0
    )

    fig2, ax2 = plt.subplots()

    summary.plot(
        kind="bar",
        ax=ax2,
        color=["green", "red"]
    )

    plt.title("Income vs Expense")
    plt.xlabel("Type")
    plt.ylabel("Amount (₹)")

    for i, val in enumerate(summary):
        ax2.text(i, val + 5, f"{val:.0f}", ha='center')

    st.pyplot(fig2)

else:
    st.info("No data available.")

st.subheader("Monthly Financial Insights")

if not df.empty:

    df["Date"] = pd.to_datetime(df["Date"])

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly_summary = df.groupby(
        ["Month", "Type"]
    )["Amount"].sum().unstack(fill_value=0)

    if "Income" not in monthly_summary.columns:
        monthly_summary["Income"] = 0

    if "Expense" not in monthly_summary.columns:
        monthly_summary["Expense"] = 0

    monthly_summary["Savings"] = (
        monthly_summary["Income"] - monthly_summary["Expense"]
    )

    monthly_summary["Savings %"] = (
        (monthly_summary["Savings"] / monthly_summary["Income"]) * 100
    ).fillna(0)

    st.dataframe(monthly_summary)

    st.subheader("Monthly Expense Trend")

    fig3, ax3 = plt.subplots()

    ax3.plot(
        monthly_summary.index,
        monthly_summary["Expense"],
        marker='o'
    )

    plt.xticks(rotation=45)

    plt.xlabel("Month")
    plt.ylabel("Expense Amount (₹)")
    plt.title("Monthly Expense Trend")

    st.pyplot(fig3)

    avg_savings = monthly_summary["Savings %"].mean()

    st.markdown(
        f"### Average Savings Percentage: {avg_savings:.2f}%"
    )

    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Download Financial Report",
        data=csv,
        file_name='finance_report.csv',
        mime='text/csv'
    )

else:
    st.info("No data available for monthly insights.")
