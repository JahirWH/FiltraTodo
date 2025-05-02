from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CURRENT_FILE'] = None  # Variable para almacenar el archivo actual

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        return jsonify({'error': 'Only CSV and Excel files are supported'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Almacenar la ruta del archivo actual
    app.config['CURRENT_FILE'] = file_path

    return jsonify({'message': 'Archivo subido correctamente', 'file_path': file_path})

@app.route('/filter', methods=['POST'])
def filter_data():
    data = request.json
    filter_type = data.get('filter_type')

    if not app.config['CURRENT_FILE']:
        return jsonify({'error': 'No hay archivo cargado para filtrar'}), 400

    try:
        # Determinar el tipo de archivo y cargarlo con pandas
        file_path = app.config['CURRENT_FILE']
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:  # Excel
            df = pd.read_excel(file_path)

        # Obtener información de columnas y datos filtrados
        columns = df.columns.tolist()

        filtered_data = None
        message = ""

        if filter_type == 'name':
            # Buscar columnas que puedan contener nombres
            name_columns = [col for col in columns if any(s in col.lower() for s in ['nombre', 'name', 'apellido', 'last'])]
            if name_columns:
                # Ordenar por la primera columna de nombre encontrada
                df = df.sort_values(by=name_columns[0])
                message = f"Datos filtrados por {name_columns[0]}"

            else:
                message = "No se encontraron columnas de nombres"

        elif filter_type == 'age':
            # Buscar columnas que puedan contener edades
            age_columns = [col for col in columns if any(s in col.lower() for s in ['edad', 'age', 'años'])]
            if age_columns:
                # Ordenar por la primera columna de edad encontrada
                df = df.sort_values(by=age_columns[0])
                message = f"Datos filtrados por {age_columns[0]}"
            else:
                message = "No se encontraron columnas de edad"

        elif filter_type == 'date':
            # Buscar columnas que puedan contener fechas
            date_columns = [col for col in columns if any(s in col.lower() for s in ['fecha', 'date', 'día', 'day'])]
            if date_columns:
                # Ordenar por la primera columna de fecha encontrada
                df = df.sort_values(by=date_columns[0])
                message = f"Datos filtrados por {date_columns[0]}"
            else:
                message = "No se encontraron columnas de fecha"

        elif filter_type == 'email':
            #Busca si tiene un @ y o un .com .
            email_columns = [col for col in columns if any(s in col.lower() for s in ['email','correo','gmail'])]
            if email_columns :
                df = df.sort_values(by=email_columns[0])
                message = f"Datos filtraos por {email_columns[0]}"
            else:
                message = f"No se encontraron columnas de {filter_type}"

        # Guardar datos filtrados en un nuevo archivo
        filtered_file = f"filtered_{filter_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filtered_path = os.path.join(app.config['UPLOAD_FOLDER'], filtered_file)
        df.to_csv(filtered_path, index=False)

        return jsonify({
            'message': message,
            'filtered_file': filtered_file,
            'row_count': len(df),
            'preview': df.head(5).to_dict('records')
        })

    except Exception as e:
        return jsonify({'error': f'Error al filtrar datos: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
