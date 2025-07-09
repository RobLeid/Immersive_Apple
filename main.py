import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

today = date.today()

def process_files(file1, file2):
    # Read files
    df1 = pd.read_csv(file1, sep='\t', encoding='latin-1')
    df2 = pd.read_csv(file2, sep='\t', encoding='latin-1')

    # Strip whitespace from column names
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Select relevant columns
    selected_columns = [
        'Track_adam_id',
        'Track_Vendor_id',
        'Track_Title',
        'Primary_Artist_Name',
        'Playlist_UPC',
        'Immersive Audio'
    ]
    df1 = df1[selected_columns]
    df2 = df2[selected_columns]

    # Merge dataframes
    merged_df = df1.merge(
        df2,
        on=[
            'Track_adam_id',
            'Track_Vendor_id',
            'Track_Title',
            'Primary_Artist_Name',
            'Playlist_UPC'
        ],
        suffixes=('_df1', '_df2')
    )

    # Identify changes
    changed_to_zero = merged_df[
        (merged_df['Immersive Audio_df1'] == 1) &
        (merged_df['Immersive Audio_df2'] == 0)
    ]

    added_to_Apple = merged_df[
        (merged_df['Immersive Audio_df1'] == 0) &
        (merged_df['Immersive Audio_df2'] == 1)
    ]

    return changed_to_zero, added_to_Apple

def to_excel(df):
    """
    Converts a pandas DataFrame to an Excel file in memory.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=f'{today}')
    return output.getvalue()

# Streamlit UI
st.title('Apple Immersive Analyzer')

uploaded_file1 = st.file_uploader("Upload old report", type=['txt'])
uploaded_file2 = st.file_uploader("Upload current report", type=['txt'])

if uploaded_file1 is not None and uploaded_file2 is not None:
    st.success("Files uploaded successfully!")
    
    # Process files
    changed_to_zero, added_to_Apple = process_files(uploaded_file1, uploaded_file2)

    # Preview results
    st.subheader("Preview of Removals")
    st.dataframe(changed_to_zero.head())

    st.subheader("Preview of Additions")
    st.dataframe(added_to_Apple.head())

    # Download buttons
    st.download_button(
        label="Download REMOVALS",
        data=to_excel(changed_to_zero),
        file_name=f'immersive_removals_apple_{today}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

    st.download_button(
        label="Download ADDITIONS",
        data=to_excel(added_to_Apple),
        file_name=f'immersive_additions_apple_{today}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
