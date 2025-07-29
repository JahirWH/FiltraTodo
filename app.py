from flask import Flask, request, jsonify, render_template, send_from_directory, session
import os
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no encontrado'}), 400

        file = request.files['file']

        # Verificar que el archivo tiene nombre
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400

        # Usar secure_filename para seguridad
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['CURRENT_FILE'] = filepath

        # Validación por extensión usando filename
        if filename.lower().endswith('.csv'):
            try:
                # Intentar leer con diferentes encodings
                encodings = ['utf-8', 'latin-1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding, nrows=1)  # Solo leer primera fila para validar
                        break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError):
                        continue
                
                if df is None or df.empty:
                    return jsonify({'error': 'El archivo CSV está vacío o no se puede leer'}), 400
                
                # Leer el archivo completo para obtener información
                df_full = pd.read_csv(filepath, encoding=encoding)
                
                return jsonify({
                    'mensaje': 'Archivo CSV cargado correctamente',
                    'filas': len(df_full),
                    'columnas': len(df_full.columns),
                    'nombres_columnas': df_full.columns.tolist()
                })
                
            except Exception as e:
                return jsonify({'error': f'Error al procesar CSV: {str(e)}'}), 400

        elif filename.lower().endswith(('.xlsx', '.xls')):
            try:
                print(f"Abriendo archivo Excel: {filepath}")
                
                # Verificar que el archivo se puede abrir
                with pd.ExcelFile(filepath) as xls:
                    if not xls.sheet_names:
                        return jsonify({'error': 'El archivo Excel no contiene hojas'}), 400
                    
                    # Leer la primera hoja para validar
                    df = pd.read_excel(filepath, sheet_name=0)
                    
                    if df.empty:
                        return jsonify({'error': 'El archivo Excel está vacío'}), 400
                    
                    return jsonify({
                        'mensaje': 'Archivo Excel cargado correctamente',
                        'hojas': xls.sheet_names,
                        'filas': len(df),
                        'columnas': len(df.columns),
                        'nombres_columnas': df.columns.tolist()
                    })
                    
            except Exception as e:
                return jsonify({'error': f'Error al procesar Excel: {str(e)}'}), 400
        else:
            return jsonify({'error': 'Extensión de archivo no soportada. Use CSV, XLS o XLSX'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/filter', methods=['POST'])
def filter_data():
    try:
        # Verificar que se enviaron datos
        if not request.json:
            return jsonify({'error': 'No se enviaron datos JSON'}), 400
            
        data = request.json
        filter_type = data.get('filter_type')

        if not filter_type:
            return jsonify({'error': 'Tipo de filtro no especificado'}), 400

        # Verificar que hay archivo cargado
        if not session.get('CURRENT_FILE'):
            return jsonify({'error': 'No hay archivo cargado para filtrar'}), 400

        file_path = session.get('CURRENT_FILE')
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            return jsonify({'error': 'El archivo ya no existe'}), 400

        # Determinar el tipo de archivo y cargarlo con pandas
        try:
            if file_path.lower().endswith('.csv'):
                # Intentar con diferentes encodings
                encodings = ['utf-8', 'latin-1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                        
                if df is None:
                    return jsonify({'error': 'No se pudo leer el archivo CSV'}), 400
            else:  # Excel
                df = pd.read_excel(file_path)
                
        except Exception as e:
            return jsonify({'error': f'Error al leer archivo: {str(e)}'}), 400

        # Obtener información de columnas
        columns = df.columns.tolist()
        print(f"Columnas encontradas: {columns}")

        message = ""
        columna_usada = None

        # CORRECCIÓN: Usar strings en lugar de listas para comparación
        if filter_type == 'name':
            # Buscar columnas que puedan contener nombres
            name_patterns = ['nombre', 'name', 'apellido', 'last', 'first', 'firstname', 'lastname']
            name_columns = [col for col in columns if any(pattern in col.lower() for pattern in name_patterns)]
            
            if name_columns:
                columna_usada = name_columns[0]
                df = df.sort_values(by=columna_usada)
                message = f"Datos ordenados por {columna_usada}"
            else:
                message = "No se encontraron columnas de nombres"

        elif filter_type == 'age':
            # Buscar columnas que puedan contener edades
            age_patterns = ['edad', 'age', 'años', 'year']
            age_columns = [col for col in columns if any(pattern in col.lower() for pattern in age_patterns)]
            
            if age_columns:
                columna_usada = age_columns[0]
                df = df.sort_values(by=columna_usada)
                message = f"Datos ordenados por {columna_usada}"
            else:
                message = "No se encontraron columnas de edad"

        elif filter_type == 'date':
            # Buscar columnas que puedan contener fechas
            date_patterns = ['fecha', 'date', 'día', 'day']
            date_columns = [col for col in columns if any(pattern in col.lower() for pattern in date_patterns)]
            
            if date_columns:
                columna_usada = date_columns[0]
                df = df.sort_values(by=columna_usada)
                message = f"Datos ordenados por {columna_usada}"
            else:
                message = "No se encontraron columnas de fecha"

        elif filter_type == 'email':
            # CORRECCIÓN: Buscar columnas de email correctamente
            email_patterns = ['email', 'correo', 'gmail', 'mail']
            email_columns = [col for col in columns if any(pattern in col.lower() for pattern in email_patterns)]
            
            if email_columns:
                columna_usada = email_columns[0]
                df = df.sort_values(by=columna_usada)
                message = f"Datos ordenados por {columna_usada}"
            else:
                message = "No se encontraron columnas de email"

        elif filter_type == 'city':  # CORRECCIÓN: Usar string en lugar de lista
            # Buscar columnas de ciudad
            city_patterns = ['ciudad', 'city', 'town', 'localidad', 'country']
            city_columns = [col for col in columns if any(pattern in col.lower() for pattern in city_patterns)]
            
            if city_columns:
                columna_usada = city_columns[0]
                df = df.sort_values(by=columna_usada)
                message = f"Datos ordenados por {columna_usada}"
            else:
                message = "No se encontraron columnas de ciudad"

        elif filter_type == 'phone':  # CORRECCIÓN: Usar string en lugar de lista
            # Buscar columnas de teléfono
            phone_patterns = ['teléfono', 'telefono', 'phone', 'número', 'numero', 'number']
            phone_columns = [col for col in columns if any(pattern in col.lower() for pattern in phone_patterns)]
            
            if phone_columns:
                columna_usada = phone_columns[0]
                df = df.sort_values(by=columna_usada)
                message = f"Datos ordenados por {columna_usada}"
            else:
                message = "No se encontraron columnas de teléfono"
        
        else:
            return jsonify({'error': f'Tipo de filtro "{filter_type}" no soportado'}), 400

        # Guardar datos filtrados en un nuevo archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filtered_file = f"filtered_{filter_type}_{timestamp}.csv"
        filtered_path = os.path.join(app.config['UPLOAD_FOLDER'], filtered_file)
        
        try:
            df.to_csv(filtered_path, index=False, encoding='utf-8')
        except Exception as e:
            return jsonify({'error': f'Error al guardar archivo: {str(e)}'}), 500

        # Preparar datos de preview
        try:
            preview_data = df.head(5).fillna('').to_dict('records')
        except Exception as e:
            preview_data = []
            print(f"Error en preview: {e}")

        return jsonify({
            'message': message,
            'filtered_file': filtered_file,
            'row_count': len(df),
            'column_used': columna_usada,
            'preview': preview_data
        })

    except Exception as e:
        print(f"Error en filter_data: {str(e)}")
        return jsonify({'error': f'Error al filtrar datos: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def download_file(filename):
    try:
        # Usar secure_filename para seguridad
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error al descargar: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)