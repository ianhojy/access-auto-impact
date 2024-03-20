import pandas as pd
from scipy import stats
import warnings
import numpy as np
import streamlit as st

warnings.filterwarnings('ignore')

def get_results(filename, num_pre_cols, num_post_cols, min_val, max_val, question_categories):


    st.subheader(':grey[Pre-Checks]')
    df = pd.read_excel(filename)
    if num_post_cols != 0:
        df = df.iloc[:, num_pre_cols: -num_post_cols]
    else:
        df = df.iloc[:, num_pre_cols:]
    num_cols = len(df.columns)
    st.write(num_cols)

    num_cols_even = num_cols % 2 == 0
    if num_cols_even:
        st.write(':grey[✅ Number of remaining columns are even]')

    num_pre_post_qns = int(num_cols/2)
    st.write(f':grey[✅ There are {num_pre_post_qns} pre-post questions]')
    if num_pre_post_qns == sum(question_categories.values()):
        st.write(f':grey[✅ Category Qn Counts sum up to expected number of questions]')

    unique_vals = set(df.stack().unique())
    if unique_vals <= set(range(min_val, max_val+1)):
        st.write(f':grey[✅ Unique response values are within range]')

    def get_confidence_of_difference(array1, array2):
        _, p_value = stats.ttest_ind(array1, array2)
        return round(100 * (1 - p_value), 1)

    def make_square_dataframe(df, num_qns=1):
        
        new_index = list(range(1, num_qns*6+1))
        new_columns = list(range(1, num_qns*6+1))

    
        missing_rows = [r for r in new_index if r not in df.index]
        missing_columns = [c for c in new_columns if c not in df.columns]
        
        for row in missing_rows:
            df.loc[row] = 0
        
        for col in missing_columns:
            df[col] = 0
        
        df = df.sort_index(axis=0)
        df = df.sort_index(axis=1)
        
        return df

    def get_breakdown(res, num_qns=1):

        improve = 0
        decline = 0
        same_low = 0
        same_high = 0
        total = 0
        
        max_val = num_qns * 6

        for row in range(1, max_val + 1, 1):
            for col in range(1, max_val + 1, 1):
                val = res.loc[row, col]
                if col > row:
                    improve += val
                elif col < row:
                    decline += val
                elif col == row:
                    if col <= max_val / 2:
                        same_low += val
                    else:
                        same_high += val                
                else:
                    raise Exception('False Logic')

                total += val
                
        return {
            'improve': improve, 
            'decline': decline, 
            'same_low': same_low, 
            'same_high': same_high, 
            'total': total
        }

    results = dict()

    bef_index = 0

    for cat, num_qns in question_categories.items():
        
        inner_results = list()
        
        for _ in range(num_qns):
            
            inner_dict = dict()
            
            aft_index = bef_index + 1
            
            bef_qn = df.columns[bef_index]
            aft_qn = df.columns[aft_index]
            
            inner_dict['before_qn'] = bef_qn
            inner_dict['after_qn'] = aft_qn
            
            
            temp = df.iloc[:, [bef_index, aft_index]]
            temp.rename(columns={
                bef_qn: 'before',
                aft_qn: 'after'
            }, inplace=True)
            
            before_mean = round(temp['before'].mean(), 2)
            after_mean = round(temp['after'].mean(), 2)
            abs_change = round(after_mean - before_mean, 2)
            pct_change = round((abs_change / before_mean) * 100, 1)
            confidence_diff = get_confidence_of_difference(temp['before'], temp['after'])
            
            inner_dict.update({
                'before_mean': before_mean,
                'after_mean': after_mean,
                'abs_change': abs_change,
                'pct_change': pct_change,
                'confidence_diff': confidence_diff
            })
            
            
            groupby_temp = make_square_dataframe(
                temp.groupby(['before', 'after'])
                    .size()
                    .unstack()
                    .fillna(0)
                    .astype(int)
            )
            
            inner_dict.update(get_breakdown(groupby_temp))
            
            inner_results.append(inner_dict)
            
            bef_index += 2
            
        cat_start_index = aft_index - 2 * num_qns + 1
        
        cat_before = df.iloc[:, np.arange(
            cat_start_index, 
            cat_start_index + num_qns * 2, 2)].sum(axis=1)
        
        cat_after = df.iloc[:, np.arange(
            cat_start_index + 1, 
            cat_start_index + num_qns * 2 + 1, 2)].sum(axis=1)

        cat_combined = pd.concat([cat_before, cat_after], axis=1).rename(
            columns={0: 'cat_before', 1: 'cat_after'})
        
        cat_groupby_temp = make_square_dataframe(
            cat_combined.groupby(['cat_before', 'cat_after'])
                .size()
                .unstack()
                .fillna(0)
                .astype(int),
        num_qns=num_qns)
            
        cat_before_mean = round(cat_combined['cat_before'].mean(), 2)
        cat_after_mean = round(cat_combined['cat_after'].mean(), 2)
        cat_abs_change = round(cat_after_mean - cat_before_mean, 2)
        cat_pct_change = round((cat_abs_change / cat_before_mean) * 100, 1)
        cat_confidence_diff = get_confidence_of_difference(
            cat_combined['cat_before'], cat_combined['cat_after'])
            
        cat_results = dict()
        
        cat_results['cat_num_qns'] = num_qns
        cat_results.update({
            'cat_before_mean': cat_before_mean,
            'cat_after_mean': cat_after_mean,
            'cat_abs_change': cat_abs_change,
            'cat_pct_change': cat_pct_change,
            'cat_confidence_diff': cat_confidence_diff
        })
        
        cat_results.update(get_breakdown(cat_groupby_temp, num_qns=num_qns))
        cat_results['question_results'] = inner_results
        
        results[cat] = cat_results

    return results