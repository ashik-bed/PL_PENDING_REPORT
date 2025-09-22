import streamlit as st
import pandas as pd
import io

# ---------------- PENDING TRACKER APP ----------------
st.set_page_config(page_title="Pending Tracker", page_icon="📊", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; color: maroon;'>📊 Pending Tracker Report Generator</h1>
    <hr style='border:1px solid maroon'>
    """,
    unsafe_allow_html=True
)

# ---------------- FILE UPLOADER ----------------
report_type = st.selectbox("Select Report Type", ["--Select--", "Pending Tracker"])
pending_file = st.file_uploader("📂 Upload Outstanding Report", type=["xlsx", "xls", "csv"])

def read_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, skiprows=1)
    elif uploaded_file.name.endswith(".xls"):
        st.error("❌ .xls files are not supported. Please convert to .xlsx")
        return None
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl", skiprows=1)
    return df

if report_type == "Pending Tracker" and pending_file:
    try:
        df = read_file(pending_file)
        if df is not None:
            df.columns = df.columns.str.strip().str.upper()

            required_cols = ["BRANCH NAME", "NEW ACCOUNT", "TOTAL OS", "PRINCIPAL OS", "CUSTOMER NAME", "CUSTOMER ID"]
            missing_cols = [c for c in required_cols if c not in df.columns]

            if missing_cols:
                st.error(f"❌ Missing columns in file: {missing_cols}")
            else:
                st.success("✅ File uploaded successfully! Scroll below to generate reports.")

                col1, col2 = st.columns(2)

                # ---------------- CONSOLIDATED REPORT ----------------
                with col1:
                    with st.expander("📊 Consolidated Report", expanded=True):
                        if st.button("Generate Consolidated Report", key="consolidated"):
                            report = df.groupby("BRANCH NAME").agg({
                                "NEW ACCOUNT": "count",
                                "TOTAL OS": "sum",
                                "PRINCIPAL OS": "sum"
                            }).reset_index()

                            report.rename(columns={
                                "NEW ACCOUNT": "New Account Count",
                                "TOTAL OS": "Total OS",
                                "PRINCIPAL OS": "Principal OS"
                            }, inplace=True)

                            st.dataframe(report, use_container_width=True)

                            # Download button
                            output = io.BytesIO()
                            report.to_excel(output, index=False, sheet_name="Consolidated Report")
                            st.download_button(
                                "⬇️ Download Consolidated Report",
                                data=output.getvalue(),
                                file_name="pending_tracker_consolidated.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                # ---------------- CUSTOMER REPORT ----------------
                with col2:
                    with st.expander("👤 Customer Report", expanded=True):
                        if st.button("Generate Customer Report", key="customer"):
                            customer_report = df[[
                                "BRANCH NAME", "NEW ACCOUNT", "CUSTOMER NAME",
                                "CUSTOMER ID", "TOTAL OS", "PRINCIPAL OS"
                            ]].copy()

                            st.dataframe(customer_report, use_container_width=True)

                            # Download button
                            output = io.BytesIO()
                            customer_report.to_excel(output, index=False, sheet_name="Customer Report")
                            st.download_button(
                                "⬇️ Download Customer Report",
                                data=output.getvalue(),
                                file_name="pending_tracker_customer.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
