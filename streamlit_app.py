import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO

# Set page config for a wide layout which is more suitable for dashboards
st.set_page_config(layout="wide", page_title="TSV Yield Calculator")

def calculate_yield(buy, sell, credit_to_customer, days_credit_given, credit_from_vendor, days_credit_availed, bank_interest, \
    additional_costs, tax_rate, desired_profit_margin):
    try:
        # Validate the sell and buy amounts
        if sell < buy:
            st.error('Sell amount should be greater than Buy amount')
            return None

        # Validate credit days
        if days_credit_given > 365 or days_credit_availed > 365:
            st.error('Credit days cannot exceed 365.')
            return None

        # Validate profit margin input
        if desired_profit_margin <= 0 or desired_profit_margin >= 100:
            st.error('Desired profit margin must be greater than 0% and less than 100%')
            return None

        # Calculate various financial metrics
        profit_before_interest = sell - buy
        yield_before_interest = (profit_before_interest / buy) * 100  # Convert to percentage
        interest_invoice = (credit_to_customer * (bank_interest/100) * days_credit_given) / 365
        interest_credit = (credit_from_vendor * (bank_interest/100) * days_credit_availed) / 365
        net_interest = interest_invoice - interest_credit
        profit_after_interest = profit_before_interest - net_interest
        yield_after_interest = (profit_after_interest / buy) * 100  # Convert to percentage
        tax_amount = profit_after_interest * (tax_rate / 100)
        profit_after_tax = profit_after_interest - tax_amount

        # Calculate the break-even sell price
        total_costs = buy + additional_costs + net_interest  # Include net interest in total costs
        break_even_sell_price = total_costs / (1 - (desired_profit_margin / 100))

        return {
            "profit_before_interest": profit_before_interest,
            "yield_before_interest": yield_before_interest,
            "net_interest": net_interest,
            "profit_after_interest": profit_after_interest,
            "yield_after_interest": yield_after_interest,
            "tax_amount": tax_amount,
            "profit_after_tax": profit_after_tax,
            "break_even_sell_price": break_even_sell_price
        }
    except Exception as e:
        st.error(f'An error occurred: {e}')
        return None

def export_to_csv(data):
    csv_file = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_file,
        file_name='yield_calculation_results.csv',
        mime='text/csv',
    )

def export_to_pdf(data):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list of lists from DataFrame for the PDF table
    data_list = [['Metric', 'Value']] + list(data.values)

    table = Table(data_list)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    table.setStyle(style)

    elems = [table]
    pdf.build(elems)

    buffer.seek(0)
    return buffer


def create_chart(data):
    fig, ax = plt.subplots(figsize=(10, 8))  # You can adjust the size as needed
    bars = ax.bar(data.keys(), data.values())
    ax.set_xlabel('Metrics')
    ax.set_ylabel('Values')
    ax.set_title('Yield Calculation Results')

    # Rotate labels and set font size
    plt.xticks(rotation=45, ha="right", fontsize=10)  # Rotate by 45 degrees and align right

    # Add data labels
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center', fontsize=8)  # Adjust font size as needed

    plt.tight_layout()  # Adjust layout to make room for label rotation
    return fig

st.title('TSV Yield Calculator') # Add a title

# Create columns for inputs to make the UI sleeker
col1, col2, col3 = st.columns(3)
with col1:
    buy = st.number_input('Buy Amount', value=100000)
    sell = st.number_input('Sell Amount', value=110000)
    credit_to_customer = st.number_input('Credit Amount to Customer', value=110000)
    desired_profit_margin = st.number_input('Desired Profit Margin (%)', min_value=0.01, max_value=99.99, value=20.00, step=0.01)
with col2:
    days_credit_given = st.number_input('No. of Days Credit Given', value=30)
    credit_from_vendor = st.number_input('Credit Availed from Vendor', value=45000)
    additional_costs = st.number_input('Additional Costs', value=0)
with col3:
    days_credit_availed = st.number_input('No. of Days Availed', value=40)
    bank_interest = st.slider('Bank OD Interest Percentage', min_value=0, max_value=20, value=12)
    tax_rate = st.slider('Tax Rate (%)', min_value=0, max_value=50, value=20)
    



# # Input fields
# inputs = ['Buy Amount', 'Sell Amount', 'Credit Amount to Customer', 'No. of Days Credit Given', 'Credit Availed from Vendor', 'No. of Days Availed', 'Bank OD Interest Percentage', 'Additional Costs', 'Tax Rate (%)']
# default_values = [100000, 110000, 110000, 30, 45000, 40, 12, 0, 20]
# help_texts = ['The amount you paid to buy the product', 'The amount you received from selling the product', 'The credit amount given to the customer', 'The number of days credit was given for', 'The credit amount availed from the vendor', 'The number of days the credit was availed for', 'The bank interest percentage for the Overdraft', 'Any additional costs incurred', 'The tax rate applicable']
# values = []

# for i, input_field in enumerate(inputs):
#     if input_field == 'Tax Rate (%)':
#         value = st.slider(input_field, 0, 50, default_values[i], help=help_texts[i])
#     elif input_field == 'Bank OD Interest Percentage':
#         value = st.slider(input_field, 0, 20, default_values[i], help=help_texts[i])
#     else:
#         value = st.number_input(input_field, value=default_values[i], help=help_texts[i])
#         if value < 0:
#             st.error(f'{input_field} cannot be negative.')
#             st.stop()
#     values.append(value)


if st.button('Calculate'):
    results = calculate_yield(buy, sell, credit_to_customer, days_credit_given, credit_from_vendor, days_credit_availed, bank_interest, additional_costs, tax_rate,desired_profit_margin)
    if results:
        # Create a DataFrame and style it for better visuals
        results_df = pd.DataFrame(results.items(), columns=['Metric', 'Value'])
        st.dataframe(results_df.style.format(subset=['Value'], formatter="{:.2f}").bar(subset=['Value'], color='lightgreen'))

        # Generate and display the chart
        chart = create_chart(results)
        st.pyplot(chart)

        # Generate CSV and PDF files and create download buttons
        export_to_csv(results_df)
        pdf_file = export_to_pdf(results_df)
        st.download_button(
            label="Download PDF",
            data=pdf_file,
            file_name='yield_calculation_results.pdf',
            mime='application/pdf',
        )