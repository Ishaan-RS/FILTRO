from flask import Flask, render_template, request, send_file, session
import pandas as pd
import os
import io
import zipfile
import shutil
import tempfile
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

fil = []

def convert_txt_to_dataframes(txt_files):
    dataframes = []
    for file in txt_files:
        names=['fld1', 'PEERID', 'fld3', 'fld4', 'fld5', 'fld7', 'fld6', 'PRIMKEY',' ']
        df = pd.read_csv(file, sep='\s+', header=None, skiprows = 2, names=names)
        df = df.drop(0)
        df = df.drop(1)

        x = list(df.keys())
        x[8] = df[x[7]].to_list()
        for i in range(len(x[8])):
                cl = (df.iloc[i]).isnull()
                if cl[names[7]]:
                    j = 7
                    while (j - 1) >= 3:
                        a = df.iat[i, j - 1]
                        df.iat[i, j] = a
                        j -= 1
                    df.iat[i, 3] = ""
        df = df.drop([" "], axis = 1)
        dataframes.append(df)
    return dataframes

def generate_summary_data(l1):
    l = l1
    ip_column_index = 6
    fld3_column_index = 2
    fld4_column_index = 3
    primkey_column_index = 7
    
    for i in range(len(l)):
        m = l[i].index[-1] - 1
        if pd.isnull(l[i].iat[m - 1, 1]):
            l[i] = l[i].drop(l[i].index[-1])
    
    # Create arrays for IP, fld3, fld4, and primkey columns
    ip_array = np.concatenate([df.iloc[:, ip_column_index].values for df in l])
    fld3_array = np.concatenate([df.iloc[:, fld3_column_index].values for df in l])
    fld4_array = np.concatenate([df.iloc[:, fld4_column_index].values for df in l])
    primkey_array = np.concatenate([df.iloc[:, primkey_column_index].values for df in l])

    # Create dictionaries to store the counts for different scenarios
    normal_scenario_counts = {}
    anomaly_scenario_counts = {}
    distinct_primkey_counts = {}
    zero_primkey_counts = {}
    distinct_primkey_zero_fld3_counts = {}
    zero_prim = 0

    for ip, fld3, fld4, primkey in zip(ip_array, fld3_array, fld4_array, primkey_array):
        # Check if IP has "0::" in fld3 and no fld4
        if fld3 == "0::" and not fld4:
            if ip in anomaly_scenario_counts:
                anomaly_scenario_counts[ip] += 1
            else:
                anomaly_scenario_counts[ip] = 1

            # Check if IP has distinct primkeys in different files and fld3 is '0::'
            if ip in distinct_primkey_zero_fld3_counts:
                distinct_primkey_zero_fld3_counts[ip].add(primkey)
            else:
                distinct_primkey_zero_fld3_counts[ip] = {primkey}

        else:
            if ip in normal_scenario_counts:
                normal_scenario_counts[ip] += 1
            else:
                normal_scenario_counts[ip] = 1

            # Check if IP has distinct primkeys in different files
            if ip in distinct_primkey_counts:
                distinct_primkey_counts[ip].add(primkey)
            else:
                distinct_primkey_counts[ip] = {primkey}

            # Check if one of the primkeys is "ZERO"
            if primkey == "y/z":
                zero_prim += 1
                #if ip in zero_primkey_counts:
                #    zero_primkey_counts[ip] += 1
                #else:
                #    zero_primkey_counts[ip] = 1

    # Create a dictionary to store the counts for normal cases
    normal_counts = {}

    # Update the scenario counts for normal cases
    for count in normal_scenario_counts.values():
        if count in normal_counts:
            normal_counts[count] += 1
        else:
            normal_counts[count] = 1

    # Create a dictionary to store the counts for anomaly cases
    anomaly_counts = {}

    # Update the scenario counts for anomaly cases
    for count in anomaly_scenario_counts.values():
        if count in anomaly_counts:
            anomaly_counts[count] += 1
        else:
            anomaly_counts[count] = 1

    # Create a copy of distinct_primkey_counts keys to avoid modification during iteration
    distinct_primkey_keys = list(distinct_primkey_counts.keys())

    # Create a dictionary to store the counts for distinct primkeys
    distinct_primkey_scenario_counts = {}
    zero_primkey_scenario_counts = {}

    

    # Update the distinct primkey counts and special cases counts
    for ip in distinct_primkey_keys:
        if ip in distinct_primkey_counts:
            primkeys = distinct_primkey_counts[ip]
            count = len(primkeys)
            if count in distinct_primkey_scenario_counts:
                distinct_primkey_scenario_counts[count] += 1
            else:
                distinct_primkey_scenario_counts[count] = 1

            # Check if one of the primkeys is "ZERO"
            if "y/z" in primkeys:
                if count in zero_primkey_scenario_counts:
                    zero_primkey_scenario_counts[count] += 1
                else:
                    zero_primkey_scenario_counts[count] = 1

    # Create a dictionary to store the counts for distinct primkeys with fld3 as '0::'
    distinct_primkey_zero_fld3_scenario_counts = {}

    # Update the distinct primkey counts with fld3 as '0::'
    for ip in distinct_primkey_zero_fld3_counts.keys():
        count = len(distinct_primkey_zero_fld3_counts[ip])
        if count in distinct_primkey_zero_fld3_scenario_counts:
            distinct_primkey_zero_fld3_scenario_counts[count] += 1
        else:
            distinct_primkey_zero_fld3_scenario_counts[count] = 1

    scenario_data = {
        "Scenario": [],
        "Count": []
    }

    ok_count = normal_counts.get(len(l), 0)


    # Calculate the total count of anomalies and 2 primkey cases
    total_anomalies = sum(anomaly_counts.values())
    total_2_primkeys = 0
    for i in range(2, len(l) + 1):
        total_2_primkeys += distinct_primkey_scenario_counts.get(i, 0) + zero_primkey_scenario_counts.get(i, 0)

    total_zero_primkeys = 0
    for i in range(2, len(l) + 1):
        total_zero_primkeys = distinct_primkey_zero_fld3_scenario_counts.get(i, 0)

    # Print the counts for each scenario for normal cases
    m = 0
    total = zero_prim
    for i in range(1, len(l)):
        scenario_data['Scenario'].append(f"IP present in {i} file(s)")
        total += normal_counts.get(i, 0) + anomaly_counts.get(i, 0)
        scenario_data['Count'].append(normal_counts.get(i, 0))
        m += anomaly_counts.get(i, 0)
        
        
    scenario_data['Scenario'].append(f"Response Errors")
    scenario_data['Count'].append(m)

    scenario_data['Scenario'].append(f"Connection Lost")
    scenario_data['Count'].append(zero_prim)
    #m = 0
    #for i in range(2, len(l) + 1):
    #    m += distinct_primkey_scenario_counts.get(i, 0)


    #scenario_data["Scenario"].append("TWO TAC")
    #scenario_data["Count"].append(m)

    total += ok_count

    scenario_data["Scenario"].append("Total Number of OK cases")
    scenario_data["Count"].append(ok_count)

    scenario_data["Scenario"].append("Total Cases")
    scenario_data["Count"].append(total)

    # Create a DataFrame from the scenario_data dictionary
    scenario_df = pd.DataFrame(scenario_data)

    # Save the DataFrame to an Excel file
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        scenario_df.to_excel(writer, index=False)

    return excel_buffer.getvalue()

@app.route('/process-files', methods=['POST'])
def process_files():
    global fil
    files = request.files.getlist('files[]')
    converted_files = []
    files1 = convert_txt_to_dataframes(files)
    fil = files1
    
    for df in files1:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        converted_files.append(output)

    if len(converted_files) > 0:
        # Create a ZIP file containing converted XLSX files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for i, converted_file in enumerate(converted_files):
                original_filename = files[i].filename
                original_filename = original_filename.split(".")
                original = original_filename[0]
                zipf.writestr(f'{original}.xlsx', converted_file.getvalue())
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, mimetype='application/zip', download_name='converted_files.zip')
    return "No Valid Files Found"


@app.route('/summary-files', methods = ['POST'])
def summary_files():
    global fil
    summary_excel_data = generate_summary_data(fil)
    
    if(fil):
        return send_file(
            io.BytesIO(summary_excel_data),
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='summary.xlsx'
        )
    
    return "INVALID ACTION"

if __name__ == '__main__':
    app.run(debug=True)