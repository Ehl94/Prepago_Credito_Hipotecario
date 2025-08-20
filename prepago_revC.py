"""
rev c [25-07-2025]:
1.- Se desgloso el codigo en funcion del requerimiento del usuario 
    a.- Desea generar un resumen de su credito hipotecario.
2.- Se optimizo el calculo del desglose mensual de amortizacion e interes.
3.- Se agrego una nueva funcion para comparar escenarios con y sin prepago y graficarlos.
"""

# Importaciones
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Funciones de Cálculo
def calculate_monthly_rate(annual_rate):
    """Convertir tasa nominal anual a tasa efectiva mensual."""
    return (1 + annual_rate / 100) ** (1 / 12) - 1

def french_amortization(principal, monthly_rate, total_months):
    """Calcular cuota mensual usando el método francés."""
    return principal * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)

# Funciones de Validación
def validate_inputs(principal, annual_rate, total_months, start_date=None, prepayments_input=None):
    """Validar parámetros de entrada."""
    if principal <= 0:
        raise ValueError("El monto/capital debe ser mayor a 0.")
    if annual_rate <= 0:
        raise ValueError("La tasa debe ser mayor a 0.")
    if total_months <= 0:
        raise ValueError("El plazo debe ser mayor a 0.")
    
    if start_date:
        try:
            start_date = pd.to_datetime(start_date)
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")
    else:
        start_date = pd.to_datetime(datetime.now().date())
    
    prepayments = {}
    if prepayments_input:
        try:
            for pair in prepayments_input.split(','):
                period, amount = pair.split(':')
                period = int(period)
                amount = float(amount) * 1000  # Convertir a UF
                if period <= 0 or amount <= 0:
                    raise ValueError("Período y monto de prepago deben ser mayores a 0.")
                prepayments[period] = amount
        except ValueError as e:
            raise ValueError(f"Error en formato de prepagos: {e}. Use 'periodo:monto,periodo:monto'.")
    
    return start_date, prepayments

# Funciones de Generación de Cronograma
def generate_schedule(principal, annual_rate, total_months, prepayments=None, start_date=None):
    """Generar cronograma de amortización con o sin prepagos, usando el método francés estándar."""
    monthly_rate = calculate_monthly_rate(annual_rate)
    monthly_payment = french_amortization(principal, monthly_rate, total_months)
    
    balance = principal
    schedule = []
    month = 0
    total_interest = 0
    total_principal = 0
    
    while balance > 0 and month < total_months:
        # Calcular interés
        interest = balance * monthly_rate
        total_interest += interest
        
        # Obtener prepago para el período
        prepayment = prepayments.get(month + 1, 0) if prepayments else 0
        
        # Calcular pago de capital
        capital_payment = monthly_payment - interest
        total_payment = monthly_payment
        
        if prepayment > 0:
            balance -= prepayment
            if balance > 0:
                monthly_payment = french_amortization(balance, monthly_rate, total_months - month - 1)
        
        balance -= capital_payment
        if balance < 0:
            capital_payment += balance
            total_payment = capital_payment + interest
            balance = 0
        
        total_principal += capital_payment
        
        # Escalar valores a miles para la salida
        display_balance = round(balance / 1000, 4)
        display_capital = round(capital_payment / 1000, 4)
        display_interest = round(interest / 1000, 4)
        display_total_payment = round(total_payment / 1000, 4)
        display_total_principal = round(total_principal / 1000, 4)
        display_total_interest = round(total_interest / 1000, 4)
        display_prepayment = round(prepayment / 1000, 4)
        
        if prepayment > 0:
            schedule.append({
                'NRO de cuota': month + 1,
                'FECHA A PAGAR': start_date + pd.offsets.MonthBegin(month) + pd.offsets.Day(9),
                'Amortizacion parcial': display_capital,
                'Acumulado Amortizacion': round(display_total_principal - display_capital, 4),
                'INTERES parcial': display_interest,
                'Acumulado de Interes': round(display_total_interest - display_interest, 4),
                'TOTAL CUOTA mensual': display_total_payment,
                'SALDO': display_balance
            })
            schedule.append({
                'NRO de cuota': month + 1,
                'FECHA A PAGAR': start_date + pd.offsets.MonthBegin(month) + pd.offsets.Day(9),
                'Amortizacion parcial': display_prepayment,
                'Acumulado Amortizacion': display_total_principal,
                'INTERES parcial': 0,
                'Acumulado de Interes': display_total_interest,
                'TOTAL CUOTA mensual': display_prepayment,
                'SALDO': round((balance + capital_payment + prepayment) / 1000, 4)
            })
        else:
            schedule.append({
                'NRO de cuota': month + 1,
                'FECHA A PAGAR': start_date + pd.offsets.MonthBegin(month) + pd.offsets.Day(9),
                'Amortizacion parcial': display_capital,
                'Acumulado Amortizacion': display_total_principal,
                'INTERES parcial': display_interest,
                'Acumulado de Interes': display_total_interest,
                'TOTAL CUOTA mensual': display_total_payment,
                'SALDO': display_balance
            })
        
        month += 1
        if balance <= 0:
            break
    
    df = pd.DataFrame(schedule)
    return df, {
        'months_saved': total_months - month,
        'interest_saved': round((french_amortization(principal, monthly_rate, total_months) * total_months - total_interest) / 1000, 4),
        'new_monthly_payment': round(monthly_payment / 1000, 4),
        'total_interest': round(total_interest / 1000, 4),
        'total_principal': round(total_principal / 1000, 4)
    }

# Funciones de Visualización
def plot_summary(df):
    """Generar gráfico único con saldo, amortización acumulada e intereses acumulados."""
    plt.figure(figsize=(10, 6))
    
    # Graficar saldo
    plt.plot(df['NRO de cuota'], df['SALDO'], label='Saldo', color='blue')
    
    # Graficar amortización acumulada
    plt.plot(df['NRO de cuota'], df['Acumulado Amortizacion'], label='Amortización acumulada', color='green')
    
    # Graficar intereses acumulados
    plt.plot(df['NRO de cuota'], df['Acumulado de Interes'], label='Intereses acumulados', color='red')
    
    plt.xlabel('Mes')
    plt.ylabel('miles de UF')
    plt.title('Evolución del Saldo, Amortización e Intereses Acumulados')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('mortgage_summary.png')
    plt.close()

def plot_simulation(df):
    """Generar gráficos de evolución de saldo y cuota."""
    plt.figure(figsize=(12, 6))
    
    # Gráfico de saldo
    plt.subplot(1, 2, 1)
    plt.plot(df[df['Amortizacion parcial'] != df['TOTAL CUOTA mensual']]['NRO de cuota'], 
             df[df['Amortizacion parcial'] != df['TOTAL CUOTA mensual']]['SALDO'], 
             label='Saldo', color='blue')
    plt.xlabel('Mes')
    plt.ylabel('Saldo (miles de UF)')
    plt.title('Evolución del Saldo')
    plt.grid(True)
    plt.legend()
    
    # Gráfico de cuota total
    plt.subplot(1, 2, 2)
    plt.plot(df[df['Amortizacion parcial'] != df['TOTAL CUOTA mensual']]['NRO de cuota'], 
             df[df['Amortizacion parcial'] != df['TOTAL CUOTA mensual']]['TOTAL CUOTA mensual'], 
             label='Cuota Total', color='green')
    plt.xlabel('Mes')
    plt.ylabel('Cuota Total (miles de UF)')
    plt.title('Evolución de la Cuota Total')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('mortgage_simulation.png')
    plt.close()

def plot_comparison(df_no_prepayment, df_prepayment):
    """Genera un gráfico comparativo de los dos escenarios."""
    plt.figure(figsize=(14, 8))

    # Trazar las curvas para el escenario sin prepago
    plt.plot(df_no_prepayment['NRO de cuota'], df_no_prepayment['SALDO'], label='Saldo (sin prepago)', color='blue', linestyle='solid')
    plt.plot(df_no_prepayment['NRO de cuota'], df_no_prepayment['Acumulado Amortizacion'], label='Amortización acumulada (sin prepago)', color='green', linestyle='solid')
    plt.plot(df_no_prepayment['NRO de cuota'], df_no_prepayment['Acumulado de Interes'], label='Intereses acumulados (sin prepago)', color='red', linestyle='solid')

    # Trazar las curvas para el escenario con prepago
    plt.plot(df_prepayment['NRO de cuota'], df_prepayment['SALDO'], label='Saldo (con prepago)', color='blue', linestyle='dashed')
    plt.plot(df_prepayment['NRO de cuota'], df_prepayment['Acumulado Amortizacion'], label='Amortización acumulada (con prepago)', color='green', linestyle='dashed')
    plt.plot(df_prepayment['NRO de cuota'], df_prepayment['Acumulado de Interes'], label='Intereses acumulados (con prepago)', color='red', linestyle='dashed')

    plt.xlabel('Mes')
    plt.ylabel('miles de UF')
    plt.title('Comparación de Escenarios: Sin Prepago vs. Con Prepago')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('mortgage_comparison.png')
    plt.close()

# Funciones de Interfaz de Usuario la 1 y la 2 *importante
def mortgage_summary():
    """Función 1: Resumen de tu crédito hipotecario actual."""
    print("\n--- Resumen de tu crédito hipotecario actual ---")
    try:
        principal = float(input("Monto del crédito (UF): "))
        annual_rate = float(input("Tasa nominal anual (%): "))
        total_months = int(input("Plazo en meses: "))
        start_date = input("Fecha de inicio (YYYY-MM-DD, dejar en blanco para hoy): ").strip() or None
        
        # Validar entradas
        start_date, _ = validate_inputs(principal, annual_rate, total_months, start_date)
        
        # Generar cronograma sin prepagos
        schedule_df, metrics = generate_schedule(principal * 1000, annual_rate, total_months, prepayments=None, start_date=start_date)
        
        # Mostrar resultados
        print("\nCronograma de Amortización:")
        print(schedule_df)
        print("\nResumen del Crédito Hipotecario:")
        print(f"Cuota mensual fija (miles de UF): {metrics['new_monthly_payment']:.4f}")
        print(f"Total intereses pagados (miles de UF): {metrics['total_interest']:.4f}")
        print(f"Total amortización (miles de UF): {metrics['total_principal']:.4f}")
        
        # Exportar a CSV
        schedule_df.to_csv('mortgage_summary.csv', index=False)
        print("\nCronograma exportado a 'mortgage_summary.csv'")
        # Exportar a Excel con manejo de error si falta openpyxl
        try:
            schedule_df.to_excel('mortgage_summary.xlsx', index=False)
            print("Cronograma exportado a 'mortgage_summary.xlsx'")
        except ImportError:
            print("Advertencia: No se pudo exportar a Excel porque falta el módulo 'openpyxl'. Instálalo con 'pip install openpyxl'.")
        
        # Generar gráfico
        plot_summary(schedule_df)
        print("Gráfico generado en 'mortgage_summary.png'")
    
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


def prepayment_plan(principal, annual_rate, total_months, annual_limit, frequency_months, start_date=None):
    """
    Genera cronograma de amortización con prepagos periódicos según límite anual y frecuencia.
    """
    monthly_rate = calculate_monthly_rate(annual_rate)
    schedule = []
    remaining_principal = principal * 1000  # Mantener escala en miles de UF
    month = 0
    total_interest = 0
    total_amortization = 0

    prepayment_amount = annual_limit * 1000 / (12 // frequency_months)
    prepayments = {}
    for i in range(frequency_months, total_months + 1, frequency_months):
        prepayments[i] = min(prepayment_amount, remaining_principal)

    while remaining_principal > 0 and month < total_months:
        month += 1
        interest = remaining_principal * monthly_rate
        monthly_payment = french_amortization(remaining_principal, monthly_rate, total_months - month + 1)
        capital_payment = min(monthly_payment - interest, remaining_principal)
        total_payment = capital_payment + interest

        prepayment = prepayments.get(month, 0)
        if prepayment > 0:
            prepayment = min(prepayment, remaining_principal - capital_payment)
            remaining_principal -= prepayment
            total_amortization += prepayment

        remaining_principal -= capital_payment
        total_amortization += capital_payment
        total_interest += interest

        if total_amortization > principal * 1000:
            total_amortization = principal * 1000

        schedule.append({
            'NRO de cuota': month,
            'FECHA A PAGAR': start_date + pd.offsets.MonthBegin(month - 1) + pd.offsets.Day(9),
            'Amortizacion parcial': round(capital_payment / 1000, 4),
            'Acumulado Amortizacion': round(total_amortization / 1000, 4),
            'INTERES parcial': round(interest / 1000, 4),
            'Acumulado de Interes': round(total_interest / 1000, 4),
            'TOTAL CUOTA mensual': round(total_payment / 1000, 4),
            'Prepago': round(prepayment / 1000, 4),
            'SALDO': round(max(remaining_principal, 0) / 1000, 4)
        })

        if remaining_principal <= 0:
            break
      
    df = pd.DataFrame(schedule)
    return df, {
        'months_saved': total_months - month,
        'interest_saved': round((french_amortization(principal * 1000, calculate_monthly_rate(annual_rate), total_months) * total_months - total_interest) / 1000, 4),
        'new_monthly_payment': round(monthly_payment / 1000, 4),
        'total_interest': round(total_interest / 1000, 4),
        'total_amortization': round(total_amortization / 1000, 4)
    }

def prepayment_plan_summary():
    """Wrapper interactivo para el plan de prepago."""
    print("\n--- Plan de prepago modular ---")
    try:
        principal = float(input("Capital inicial (UF): "))
        annual_rate = float(input("Tasa nominal anual (%): "))
        total_months = int(input("Plazo en meses: "))
        start_date = input("Fecha de inicio (YYYY-MM-DD, dejar en blanco para hoy): ").strip() or None
        annual_limit = float(input("Límite de prepago anual (UF): "))
        frequency_months = int(input("Frecuencia de prepago en meses (por ejemplo, 6 o 12): "))

        if annual_limit <= 0:
            raise ValueError("El límite anual debe ser mayor a 0.")
        if frequency_months not in [6, 12]:
            raise ValueError("Frecuencia de prepago debe ser 6 (semestral) o 12 (anual).")

        start_date, _ = validate_inputs(principal, annual_rate, total_months, start_date)

        schedule_df, metrics = prepayment_plan(principal, annual_rate, total_months, annual_limit, frequency_months, start_date)

        print("\nCronograma de Amortización (primeros 24 meses y últimos 5 meses):")
        print(schedule_df.head(24).to_string(index=False))
        print("\n...")
        print(schedule_df.tail(5).to_string(index=False))
        print("\nMétricas:")
        print(f"Meses ahorrados: {metrics['months_saved']}")
        print(f"Intereses ahorrados (UF): {metrics['interest_saved']:.4f}")
        print(f"Nueva cuota (UF): {metrics['new_monthly_payment']:.4f}")
        print(f"Intereses totales pagados (UF): {metrics['total_interest']:.4f}")
        print(f"Total amortización (UF): {metrics['total_amortization']:.4f}")

        schedule_df.to_csv('mortgage_prepayment_plan.csv', index=False)
        print("\nCronograma exportado a 'mortgage_prepayment_plan.csv'")
        # Exportar a Excel con manejo de error si falta openpyxl
        try:
            schedule_df.to_excel('mortgage_prepayment_plan.xlsx', index=False)
            print("Cronograma exportado a 'mortgage_prepayment_plan.xlsx'")
        except ImportError:
            print("Advertencia: No se pudo exportar a Excel porque falta el módulo 'openpyxl'. Instálalo con 'pip install openpyxl'.")
        plot_simulation(schedule_df)
        print("Gráficos generados en 'mortgage_simulation.png'")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def compare_scenarios_and_plot():
    """Función 3: Compara el escenario sin prepago y con prepago, y genera un gráfico."""
    print("\n--- Comparación de Escenarios ---")
    try:
        principal = float(input("Monto del crédito (UF): "))
        annual_rate = float(input("Tasa nominal anual (%): "))
        total_months = int(input("Plazo en meses: "))
        annual_limit = float(input("Límite de prepago anual (UF): "))
        frequency_months = int(input("Frecuencia de prepago en meses (por ejemplo, 6 o 12): "))
        start_date = input("Fecha de inicio (YYYY-MM-DD, dejar en blanco para hoy): ").strip() or None

        start_date_validated, _ = validate_inputs(principal, annual_rate, total_months, start_date)

        # Generar datos para ambos escenarios
        df_no_prepayment, metrics_no_prepayment = generate_schedule(principal * 1000, annual_rate, total_months, prepayments=None, start_date=start_date_validated)
        df_prepayment, metrics_prepayment = prepayment_plan(principal, annual_rate, total_months, annual_limit, frequency_months, start_date_validated)

        # Generar y guardar el gráfico comparativo
        plot_comparison(df_no_prepayment, df_prepayment)
        print("\nGráfico de comparación de escenarios generado en 'mortgage_comparison.png'")
        
        # Opcionalmente, mostrar un resumen comparativo en la consola
        print("\n--- Resumen Comparativo ---")
        print(f"Escenario Sin Prepago:")
        print(f"  - Total intereses pagados (miles de UF): {metrics_no_prepayment['total_interest']:.4f}")
        print(f"  - Total amortización (miles de UF): {metrics_no_prepayment['total_principal']:.4f}")
        print(f"Escenario Con Prepago:")
        print(f"  - Total intereses pagados (miles de UF): {metrics_prepayment['total_interest']:.4f}")
        print(f"  - Meses ahorrados: {metrics_prepayment['months_saved']}")
        print(f"  - Intereses ahorrados (miles de UF): {metrics_prepayment['interest_saved']:.4f}")


    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


def main():
    """Menú principal para seleccionar la función."""
    print("\n=== Simulador de Crédito Hipotecario ===")
    print("¿Qué función desea utilizar?")
    print("1. Resumen de tu crédito hipotecario actual")
    print("2. Plan de prepago modular (límite anual y frecuencia)")
    print("3. Comparar escenarios (sin y con prepago)")
    
    try:
        choice = input("Ingrese 1, 2 o 3: ").strip()
        if choice == '1':
            mortgage_summary()
        elif choice == '2':
            prepayment_plan_summary()
        elif choice == '3':
            compare_scenarios_and_plot()
        else:
            print("Error: Opción inválida. Por favor, ingrese 1, 2 o 3.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
