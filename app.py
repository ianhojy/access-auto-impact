import streamlit as st
import pandas as pd
from utils import get_results

# Title for the app

st.set_page_config(
    page_title='Access Auto Impact Analyzer',
    layout='wide',
    page_icon='🧠'
)
st.title('Access Auto Impact Analyzer')

# Step 1: Upload Excel file

st.subheader('1. Upload Excel File')
uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])
if uploaded_file is not None:
    internal_file_name = "temp_data/data.xlsx"
    with open(internal_file_name, "wb") as f:
        f.write(uploaded_file.read())
    st.success('File successfully saved internally')

    st.divider()

    st.subheader('2. Specify Parameters')

    # Step 2: Specify parameters
    param_1, param_2, param_3, param_4 = st.columns(4)
    with param_1:
        num_pre_cols = st.number_input('# Pre Cols', help='How many columns to left of question responses in excel sheet', min_value=0, value=4, step=1)
    with param_2:
        num_post_cols = st.number_input('# Post Cols', help='How many columns to right of question responses in excel sheet', min_value=0, value=3, step=1)
    with param_3:
        min_val = st.number_input('Survey Min Val', help='Minimum value of survey response',  min_value=0, value=1, step=1)
    with param_4:
        max_val = st.number_input('Survey Max Val', help='Maximum value of survey response', min_value=1, value=6, step=1)

    st.divider()

    st.subheader('3. Question Categories')

    # Step 3: Specify a number n and enter n number of key-value pairs
    n = st.number_input('Number of Qn Categories?', min_value=1, value=3, step=1)

    # Initialize an empty dictionary
    question_categories = {}

    # Dynamically create input fields based on user-specified n

    init_question_categories = {
        'Skills': 7,
        'Self-Perception': 6,
        'Curiosity & Aspirations': 6
    }

    cat_cols = st.columns(n)

    for i in range(n):
        with cat_cols[i]:
            if i < len(init_question_categories):
                pre_key = list(init_question_categories.keys())[i]
                pre_value = init_question_categories[pre_key]
            else:
                pre_key = ''
                pre_value = 1
            key = st.text_input(f'Category {i+1}', key=f'key_{i}', value=pre_key)
            value = st.text_input(f'# Questions for Category {i+1}', key=f'value_{i}', value=pre_value)
            question_categories[key] = int(value)

    st.divider()
    if st.button('Analyze & Get Results'):
        results = get_results(internal_file_name, num_pre_cols, num_post_cols, min_val, max_val, question_categories)

        cat_tabs = st.tabs(results.keys())
        for ii, cat in enumerate(results.keys()):
            cat_res = results[cat]
            with cat_tabs[ii]:
                st.subheader(f':blue[Category: {cat}]')
                with st.container(border=True):
                    st.write(f"No. of Question: `{cat_res['cat_num_qns']}`")
                    st.write(f"Category Pre-Average: `{cat_res['cat_before_mean']}`")
                    st.write(f"Category Post-Average: `{cat_res['cat_after_mean']}`")
                    st.write(f"Category Absolute Changee: `{cat_res['cat_abs_change']}`")
                    st.write(f"Category Percentage Change: `{cat_res['cat_pct_change']}%`")
                    st.write(f"Category Confidence in Change: `{cat_res['cat_confidence_diff']}%`")
                    st.write((
                        f"Total: `{cat_res['total']} (100%)`\n"
                        f"> Improve: `{cat_res['improve']} ({round(100*cat_res['improve']/cat_res['total'])}%)`\n\n"
                        f"> Same (@ High): `{cat_res['same_high']} ({round(100*cat_res['same_high']/cat_res['total'])}%)`\n\n"
                        f"> Same (@ Low): `{cat_res['same_low']} ({round(100*cat_res['same_low']/cat_res['total'])}%)`\n\n"
                        f"> Decline: `{cat_res['decline']} ({round(100*cat_res['decline']/cat_res['total'])}%)`\n"
                        ))
                for ii, qn_res in enumerate(cat_res['question_results']):
                    with st.expander(':blue[' + cat + f': Q{ii+1}]', expanded=False):
                        st.write(f"Before Question: `{qn_res['before_qn']}`")
                        st.write(f"After Question: `{qn_res['after_qn']}`")
                        st.write(f"Pre-Average: `{qn_res['before_mean']}`")
                        st.write(f"Post-Average: `{qn_res['after_mean']}`")
                        st.write(f"Absolute Changee: `{qn_res['abs_change']}`")
                        st.write(f"Percentage Change: `{qn_res['pct_change']}%`")
                        st.write(f"Confidence in Change: `{qn_res['confidence_diff']}%`")
                        st.write((
                            f"Total: `{qn_res['total']} (100%)`\n"
                            f"> Improve: `{qn_res['improve']} ({round(100*qn_res['improve']/qn_res['total'])}%)`\n\n"
                            f"> Same (@ High): `{qn_res['same_high']} ({round(100*qn_res['same_high']/qn_res['total'])}%)`\n\n"
                            f"> Same (@ Low): `{qn_res['same_low']} ({round(100*qn_res['same_low']/qn_res['total'])}%)`\n\n"
                            f"> Decline: `{qn_res['decline']} ({round(100*qn_res['decline']/qn_res['total'])}%)`\n"
                            ))