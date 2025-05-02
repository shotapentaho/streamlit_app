import streamlit as st

def convert_units(value, quantity_type, direction):
    if quantity_type == 'Temperature':
        return (value * 9/5 + 32) if direction == 'Celsius to Fahrenheit' else (value - 32) * 5/9
    else:
        factors = {
            'Length': 3.28084,          # meter ↔ foot
            'Mass': 2.20462,            # kilogram ↔ pound
            'Force': 0.224809,          # newton ↔ pound-force
            'Energy': 0.737562,         # joule ↔ foot-pound
            'Pressure': 0.000145038     # pascal ↔ psi
        }
        factor = factors[quantity_type]
        return value * factor if direction == 'MKS to FPS' else value / factor

def show_smaller_units(quantity_type, value, direction):
    if quantity_type == 'Mass':
        if direction == 'MKS to FPS':
            grams = value * 1000
            return f"({grams:.0f} grams)"
        else:
            kg = value / 2.20462
            grams = kg * 1000
            return f"({grams:.0f} grams)"
    elif quantity_type == 'Length':
        if direction == 'MKS to FPS':
            cm = value * 100
            return f"({cm:.0f} cm)"
        else:
            m = value / 3.28084
            cm = m * 100
            return f"({cm:.0f} cm)"
    return None

st.set_page_config(page_title=" 🔁 Units Converter", layout="wide")
st.title("🔁 MKS ↔ FPS & 🌡️ Temperature, Force, Pressure and Energy Converter")

quantity_type = st.selectbox(
    "Choose one to convert:",
    ['Length', 'Mass', 'Force', 'Energy', 'Pressure', 'Temperature']
)

# Define labels and slider ranges
if quantity_type == 'Temperature':
    direction = st.radio("Conversion direction:", ['Celsius to Fahrenheit', 'Fahrenheit to Celsius'])
    input_label = '°C' if direction == 'Celsius to Fahrenheit' else '°F'
    min_val, max_val = (-50, 100) if direction == 'Celsius to Fahrenheit' else (-60, 212)
else:
    direction = st.radio("Conversion direction:", ['MKS to FPS', 'FPS to MKS'])
    labels = {
        'Length': ('meters', 'feet'),
        'Mass': ('kilograms', 'pounds'),
        'Force': ('newtons', 'pound-force'),
        'Energy': ('joules', 'foot-pounds'),
        'Pressure': ('pascals', 'psi')
    }
    input_label = labels[quantity_type][0] if direction == 'MKS to FPS' else labels[quantity_type][1]
    min_val, max_val = 0, 1000

# Slider input
value = st.slider(f"Select value in {input_label}:", min_value=min_val, max_value=max_val, step=1)

if st.button("Convert"):
    result = convert_units(value, quantity_type, direction)

    if quantity_type == 'Temperature':
        output_label = '°F' if direction == 'Celsius to Fahrenheit' else '°C'
    else:
        output_label = labels[quantity_type][1] if direction == 'MKS to FPS' else labels[quantity_type][0]

    st.success(f"{value} {input_label} = {result:.2f} {output_label}")

    # Display additional smaller unit info if applicable
    extra_info = show_smaller_units(quantity_type, value, direction)
    if extra_info:
        st.caption(f"Also: {extra_info}")
