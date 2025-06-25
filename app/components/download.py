import json
import zipfile
import io
import streamlit as st


def render_download_section(parsed_data, dataframes, current_file):
    st.markdown("---")
    st.subheader("Download Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download JSON",
            data=json.dumps(parsed_data, indent=2),
            file_name=f"parsed_{current_file}.json",
            mime="application/json",
        )

    with col2:
        if dataframes:
            selected_section = st.selectbox(
                "Select section for CSV download:", list(dataframes.keys())
            )

            if selected_section and selected_section in dataframes:
                csv_data = dataframes[selected_section].to_csv(index=False)
                st.download_button(
                    label=f"Download {selected_section} CSV",
                    data=csv_data,
                    file_name=f"{selected_section.lower().replace(' ', '_')}_{current_file}.csv",
                    mime="text/csv",
                )

    with col3:
        if dataframes:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for section_name, df in dataframes.items():
                    csv_data = df.to_csv(index=False)
                    zip_file.writestr(
                        f"{section_name.lower().replace(' ', '_')}.csv",
                        csv_data,
                    )

            st.download_button(
                label="Download All CSV (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"all_sections_{current_file}.zip",
                mime="application/zip",
            )
