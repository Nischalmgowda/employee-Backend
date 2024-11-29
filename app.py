from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Set Matplotlib backend to 'Agg'
import matplotlib
matplotlib.use('Agg')


# Set Matplotlib backend to 'Agg'
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

def process_file(filepath):
    df = pd.read_csv(filepath, parse_dates=['Datetime'], dayfirst=True)
    df['Left'] = df['Total'] - df['Consumption']
    df['Year'] = df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    return df

def plot_graphs(df):
    graph_paths = {}
    month_tables = {}
    for year in df['Year'].unique():
        graph_paths[year] = []
        month_tables[year] = {}
        for month in range(1, 13):
            df_month = df[(df['Year'] == year) & (df['Month'] == month)]
            if not df_month.empty:
                plt.figure(figsize=(10, 6))
                plt.plot(df_month['Datetime'], df_month['Consumption'], label=f'Month {month} {year}')
                plt.xlabel('Datetime')
                plt.ylabel('Consumption')
                plt.title(f'Electricity Consumption in Month {month} {year}')
                plt.legend()
                plt.grid(True)
                graph_path = os.path.join(app.config['UPLOAD_FOLDER'], f'graph_{year}_M{month}.png')
                plt.savefig(graph_path)
                plt.close()
                graph_paths[year].append(f'graph_{year}_M{month}.png')
                month_tables[year][month] = df_month.to_html(classes='data', index=False)
    return graph_paths, month_tables

@app.route('/')
def index():
    return redirect(url_for('upload_file'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = process_file(filepath)
            graph_paths, month_tables = plot_graphs(df)
            return render_template('result.html', graph_paths=graph_paths, month_tables=month_tables, filename=file.filename)
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/predict', methods=['POST'])
def predict():
    filename = request.form['filename']
    district = request.form['district']
    ward = request.form['ward']
    date = request.form['date']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath, parse_dates=['Datetime'], dayfirst=True)
    prediction = None
    
    if district == 'Chikmaglore':
        if ward == 'Koppa':
            column_consumption = 'Consumption'
            column_total = 'Total'
        elif ward == 'Sringeri':
            column_consumption = 'Ward2_Consumption'
            column_total = 'Ward2_Total'
        elif ward == 'Tarikere':
            column_consumption = 'Ward3_Consumption'
            column_total = 'Ward3_Total'
        elif ward == 'Nrpura':
            column_consumption = 'Ward4_Consumption'
            column_total = 'Ward4_Total'
        
        selected_date = datetime.strptime(date, '%Y-%m-%d')
        df_selected_date = df[df['Datetime'] == selected_date]
        if not df_selected_date.empty:
            prediction = {
                'date': date,
                'district': district,
                'ward': ward,
                'consumption': df_selected_date[column_consumption].values[0],
                'total': df_selected_date[column_total].values[0],
                'left': df_selected_date[column_total].values[0] - df_selected_date[column_consumption].values[0]
            }
    
    return render_template('prediction.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)                                                                                                                                    