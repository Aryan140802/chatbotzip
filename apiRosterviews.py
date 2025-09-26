import os
import pandas as pd
import numpy as np
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
import datetime

class FileUploadView(APIView):
    """
    Handles the uploading of multiple Excel files.
    """
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)

        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        uploaded_files = []
        for f in files:
            if not f.name.endswith(('.xls', '.xlsx')):
                return Response(
                    {'error': f'File "{f.name}" is not a valid Excel file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            filename = fs.save(f.name, f)
            uploaded_files.append(filename)
        return Response(
            {'message': f'{len(uploaded_files)} files uploaded successfully', 'files': uploaded_files},
            status=status.HTTP_201_CREATED
        )

class SearchView(APIView):
    """
    Handles searching within uploaded Excel files. It intelligently adapts to different
    file structures and performs a linked search between roster and timesheet files.
    """
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', None)
        start_date_str = request.query_params.get('start_date', None)
        end_date_str = request.query_params.get('end_date', None)

        if not query and not start_date_str:
            return Response(
                {'error': 'A search parameter "q" or "start_date" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        upload_dir = settings.MEDIA_ROOT
        if not os.path.exists(upload_dir) or not os.listdir(upload_dir):
            return Response({'message': 'No files have been uploaded yet.'}, status=status.HTTP_200_OK)

        all_results = []
        roster_files_data = []
        timesheet_files_data = []

        # First, categorize files and load their dataframes
        for filename in os.listdir(upload_dir):
            if not filename.endswith(('.xls', '.xlsx')):
                continue
            file_path = os.path.join(upload_dir, filename)
            try:
                xls = pd.read_excel(file_path, sheet_name=None, header=None)
                for sheet_name, df in xls.items():
                    header_row_index = df.dropna(how='all').index.min()
                    if pd.isna(header_row_index): continue

                    df.columns = df.iloc[header_row_index]
                    df = df.drop(header_row_index)
                    df.columns = df.columns.map(str)
                    df.reset_index(drop=True, inplace=True)
                    df.dropna(how='all', inplace=True)

                    file_info = {'df': df, 'filename': filename, 'sheet_name': sheet_name}
                    if 'date' in [c.lower() for c in df.columns]:
                        timesheet_files_data.append(file_info)
                    else:
                        roster_files_data.append(file_info)
            except Exception as e:
                all_results.append({'file': filename, 'error': f'Could not process file. Error: {str(e)}'})

        # Step 1: Process roster files to get results and a set of matched names
        roster_matched_names = set()
        for file_info in roster_files_data:
            roster_results, names = self._search_roster_format(
                file_info['df'], file_info['filename'], file_info['sheet_name'],
                query, start_date_str, end_date_str
            )
            all_results.extend(roster_results)
            roster_matched_names.update(names)

        # Step 2: Process timesheet files, passing in the names from the roster search
        for file_info in timesheet_files_data:
            timesheet_results = self._search_timesheet_format(
                file_info['df'], file_info['filename'], file_info['sheet_name'],
                query, start_date_str, end_date_str,
                names_to_include=roster_matched_names
            )
            all_results.extend(timesheet_results)

        if not all_results:
            return Response({'message': 'No results found matching your criteria.'}, status=status.HTTP_200_OK)

        return Response(all_results, status=status.HTTP_200_OK)

    def _search_timesheet_format(self, df, filename, sheet_name, query, start_date_str, end_date_str=None, names_to_include=None):
        results = []
        date_col = next((col for col in df.columns if col.lower() == 'date'), None)
        name_col = next((col for col in df.columns if col.lower() == 'name'), None)
        if not date_col or not name_col:
            return results

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df.dropna(subset=[date_col], inplace=True)

        filtered_df = df.copy()

        if start_date_str:
            try:
                start_date = pd.to_datetime(start_date_str)
                if end_date_str:
                    end_date = pd.to_datetime(end_date_str)
                    date_mask = (filtered_df[date_col].dt.date >= start_date.date()) & (filtered_df[date_col].dt.date <= end_date.date())
                else:
                    date_mask = filtered_df[date_col].dt.date == start_date.date()
                filtered_df = filtered_df[date_mask]
            except (ValueError, TypeError):
                pass

        # Combine query search with name-based search
        query_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
        if query:
            df_str = filtered_df.astype(str)
            query_mask = df_str.apply(lambda row: row.str.contains(query, na=False, case=False).any(), axis=1)

        name_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
        if names_to_include and name_col in filtered_df.columns:
            name_mask = filtered_df[name_col].isin(names_to_include)

        if query or names_to_include:
            filtered_df = filtered_df[query_mask | name_mask]

        filtered_df = filtered_df.replace({np.nan: None})
        for index, row in filtered_df.iterrows():
            formatted_row = row.apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.datetime, pd.Timestamp)) else x)
            results.append({
                'file': filename, 'sheet': sheet_name, 'type': 'Timesheet Record', 'data': formatted_row.to_dict()
            })
        return results

    def _search_roster_format(self, df, filename, sheet_name, query, start_date_str, end_date_str=None):
        results = []
        matched_names = set()
        name_col = next((col for col in df.columns if col.lower() == 'name'), None)
        if not name_col:
            return results, matched_names

        df.dropna(subset=[name_col], inplace=True)

        # Case 1: Name search, NO date provided
        if query and not start_date_str:
            filtered_df = df[df[name_col].str.contains(query, na=False, case=False)]
            day_cols = [col for col in df.columns if col.isdigit()]
            for index, row in filtered_df.iterrows():
                matched_names.add(row[name_col])
                for day in day_cols:
                    schedule = row.get(day)
                    if pd.isna(schedule): schedule = None
                    date_str = f"2025-07-{int(day):02d}"
                    results.append({
                        'file': filename, 'sheet': sheet_name, 'type': 'Roster Schedule',
                        'data': {'name': row[name_col], 'date': date_str, 'schedule': schedule}
                    })
            return results, matched_names

        if not start_date_str:
            return [], set()

        # Case 2: Date is provided
        try:
            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str) if end_date_str else start_date
        except (ValueError, TypeError):
            return [], set()

        for date in pd.date_range(start=start_date, end=end_date):
            day_of_month_col = str(date.day)
            if day_of_month_col in df.columns:
                for index, row in df.iterrows():
                    roster_value = row.get(day_of_month_col)
                    if pd.isna(roster_value): roster_value = None

                    is_match = False
                    if not query:
                        is_match = True
                    else:
                        if query.lower() in str(row[name_col]).lower() or query.lower() in str(roster_value).lower():
                            is_match = True

                    if is_match:
                        matched_names.add(row[name_col])
                        results.append({
                            'file': filename, 'sheet': sheet_name, 'type': 'Roster Schedule',
                            'data': {'name': row[name_col], 'date': date.strftime('%Y-%m-%d'), 'schedule': roster_value}
                        })
        return results, matched_names
