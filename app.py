from flask import Flask, render_template, request

app = Flask(__name__)

def gravity_correction(latitude, elevation, observed_gravity, correction_type):
    G = 6.67430e-11
    equatorial_radius = 6378137.0
    polar_radius = 6356752.0
    geocentric_gravity = 9.7803267714
    density_of_earth = 5515

    if correction_type == 'free_air':
        free_air_correction = 0.3086 * elevation
        corrected_gravity = observed_gravity + free_air_correction

    elif correction_type == 'bouguer':
        bouguer_correction = 0.0419 * elevation
        corrected_gravity = observed_gravity + bouguer_correction

    elif correction_type == 'terrain':
        terrain_correction = 0.0419 * elevation - 0.1036 * elevation**2
        corrected_gravity = observed_gravity + terrain_correction

    elif correction_type == 'eotvos':
        omega = 7.292115e-5
        eotvos_correction = 0.031 * latitude * (omega**2) * (equatorial_radius**2) * (polar_radius**2) / G
        corrected_gravity = observed_gravity + eotvos_correction

    elif correction_type == 'latitude':
        latitude_correction = 0.0053024 * (latitude**2) + 0.0000058 * (latitude**4)
        corrected_gravity = observed_gravity + latitude_correction

    elif correction_type == 'igf':
        latitude_radians = latitude * (3.14159265359 / 180.0)
        height_ratio = elevation / 1000.0
        igf_correction = geocentric_gravity * ((1 + 0.00193185138639 * (latitude_radians**2)) /
                                               (1 - 0.00264639562867 * (latitude_radians**2)) - 1) * height_ratio
        corrected_gravity = observed_gravity + igf_correction

    else:
        raise ValueError("Invalid gravity correction type.")
    
    return corrected_gravity

def calculate_resistivity(method, a, b, n, d):
    if method == 'Wenner':
        resistivity = (2 * 3.14 * a * n) / (d * (a**2 - b**2))
    elif method == 'Schlumberger':
        resistivity = (3.14 * a**2 * n) / (2 * d)
    elif method == 'Pole-Pole':
        resistivity = (2 * 3.14 * a * n) / (d * (a + b))
    elif method == 'Pole-Dipole':
        resistivity = (3.14 * a**2 * n) / (d * (2 * a - b))
    else:
        raise ValueError("Invalid resistivity calculation method.")

    return resistivity

@app.route('/', methods=['GET', 'POST'])
def index():
    corrected_gravity = None
    resistivity = None

    if request.method == 'POST':
        method = request.form['method']
        latitude = float(request.form['latitude'])
        elevation = float(request.form['elevation'])
        observed_gravity = float(request.form['observed_gravity'])
        correction_type = request.form['correction_type']

        if correction_type:
            corrected_gravity = gravity_correction(latitude, elevation, observed_gravity, correction_type)
            
        a = float(request.form['a'])
        b = float(request.form['b'])
        n = int(request.form['n'])
        d = float(request.form['d'])
        
        if method:
            resistivity = calculate_resistivity(method, a, b, n, d)
    
    return render_template('index.html', corrected_gravity=corrected_gravity, resistivity=resistivity)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    