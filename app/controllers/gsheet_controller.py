import gspread
import pandas as pd
from dotenv import load_dotenv
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()
GS_CONFIG = os.getenv("GS_CONFIG")
GS_FILE = os.getenv("GS_FILE")

class GoogleSheet:

    def __init__(self):
        self.gc = gspread.service_account(filename=GS_CONFIG)
        self.sh = self.gc.open(GS_FILE)

    def get_budget_payment_link_message(self, budget_id, amount, currency):

        try:
            budget_sheet = self.sh.worksheet('Presupuestos')
            data_budget = budget_sheet.get_all_records()
            df_budget = pd.DataFrame(data_budget)
            budget = df_budget[df_budget['numero_presupuesto'] == int(budget_id)]

            float_amount = float(amount)

            if budget.empty:
                return f"El presupuesto {budget_id} no existe"
            
            row_number = budget.index[0]

            if float_amount == 0:
                link_amount = budget.loc[row_number, 'monto']
            elif budget.loc[row_number, 'moneda'] != currency:
                return f"Error en la moneda, la moneda del presupuesto es {budget.loc[budget.index, 'moneda']} y el monto a pagar esta en {currency}"
            elif float(budget.loc[row_number, 'monto']) < float_amount:
                return f"Error en el monto, el monto del presupuesto {budget_id} es {budget.loc[row_number, 'monto']} {budget.loc[row_number, 'moneda']}"
            else:
                link_amount = float_amount

            provider_sheet = self.sh.worksheet('Proveedores')
            data_providers = provider_sheet.get_all_records()
            df_provider = pd.DataFrame(data_providers)
            provider = df_provider[df_provider['numero_proveedor'] == budget.loc[row_number, 'numero_proveedor']]

            if provider.empty:
                return f"El proveedor {budget.loc[row_number, 'numero_proveedor']} no existe"
            
            provider_name = provider.loc[row_number, 'nombre']
            bank = provider.loc[row_number, 'banco']
            p_currency = provider.loc[row_number, 'moneda']
            account = provider.loc[row_number, 'cuenta']
            beneficiary = provider.loc[row_number, 'titular']

            return f"*Información para el pago*\n\n*Proveedor*: {provider_name}\n*Monto*: {link_amount} {currency}\n*Banco*: {bank}\n*Moneda de la cuenta*: {p_currency}\n*Cuenta*: {account}\n*Titular*: {beneficiary}\n*Referencia*: {budget_id}\n\n*IMPORTANTE*: agregar la referencia indicada en la transferencia"
        except ValueError:
            return f"El id {budget_id} no representa un número entero válido"
        
    def get_provider_payment_link_message(self, provider_id, amount, currency):

        try:
            float_amount = float(amount)

            provider_sheet = self.sh.worksheet('Proveedores')
            data_providers = provider_sheet.get_all_records()
            df_provider = pd.DataFrame(data_providers)
            provider = df_provider[df_provider['numero_proveedor'] == int(provider_id)]

            if provider.empty:
                return f"El proveedor {provider.loc[row_number, 'numero_proveedor']} no existe"
            
            row_number = provider.index[0]
            provider_name = provider.loc[row_number, 'nombre']
            bank = provider.loc[row_number, 'banco']
            p_currency = provider.loc[row_number, 'moneda']
            account = provider.loc[row_number, 'cuenta']
            beneficiary = provider.loc[row_number, 'titular']

            return f"*Información para el pago*\n\n*Proveedor*: {provider_name}\n*Monto*: {float_amount} {currency}\n*Banco*: {bank}\n*Moneda de la cuenta*: {p_currency}\n*Cuenta*: {account}\n*Titular*: {beneficiary}\n*Referencia*: {provider_id}\n\n*IMPORTANTE*: agregar la referencia indicada en la transferencia"
        except ValueError:
            return f"El id {provider_id} no representa un número entero válido"
    
    def reconcile_payment(self, budget_id, amount, currency):

        budget_sheet = self.sh.worksheet('Presupuestos')
        data_budget = budget_sheet.get_all_records()
        df_budget = pd.DataFrame(data_budget)
        budget = df_budget[df_budget['numero_presupuesto'] == int(budget_id)]

        float_amount = float(amount)
        row_number = budget.index[0]
        
        if budget.empty:
            return f"El presupuesto {budget_id} no existe, si queres unicamente guardar el pago, usa /pago"
        elif budget.loc[row_number, 'moneda'] != currency:
                return f"Error en la moneda, la moneda del presupuesto es {budget.loc[row_number, 'moneda']} y el monto a pagar esta en {currency}"
        elif float(budget.loc[row_number, 'monto_pendiente']) < float_amount:
            return f"Error en el monto, el monto del presupuesto {budget_id} es {budget.loc[row_number, 'monto_pendiente']}"
        else:
            payments_sheet = self.sh.worksheet('Pagos')
            id_payment = len(payments_sheet.get_all_values()) + 1

            data = payments_sheet.get_all_values()
            range_start = "A{}".format(id_payment)
            letter_end = chr(ord('A') + len(data[0]) - 1)
            range_end = "{}{}".format(letter_end, id_payment)
            
            payments_sheet.update("{}:{}".format(range_start,range_end), [[id_payment, currency, float_amount, int(budget_id), ""]])
            return "El pago fue conciliado correctamente"

    def add_payment(self, provider_id, amount, currency):
        provider_sheet = self.sh.worksheet('Proveedores')
        data_provider = provider_sheet.get_all_records()
        df_provider = pd.DataFrame(data_provider)
        provider = df_provider[df_provider['numero_proveedor'] == int(provider_id)]

        float_amount = float(amount)
        row_number = provider.index[0]

        if provider.empty:
            return f"El proveedor {provider_id} no existe"
        else:
            payments_sheet = self.sh.worksheet('Pagos')
            id_payment = len(payments_sheet.get_all_values()) + 1

            data = payments_sheet.get_all_values()
            range_start = "A{}".format(id_payment)
            letter_end = chr(ord('A') + len(data[0]) - 1)
            range_end = "{}{}".format(letter_end, id_payment)
            
            payments_sheet.update("{}:{}".format(range_start,range_end), [id_payment, currency, float_amount, "", int(provider_id)])

            return f"El pago a {provider.loc[row_number, 'nombre']} fue ingresado correctamente"
    
    def get_providers(self):
        provider_sheet = self.sh.worksheet('Proveedores')
        data_provider = provider_sheet.get_all_records()
        df_provider = pd.DataFrame(data_provider)
        response = ""
        for index, provider in df_provider.iterrows():
            response += f"- {provider['numero_proveedor']} {provider['nombre']}\n"

        return response
    
    def get_budgets(self):
        budget_sheet = self.sh.worksheet('Presupuestos')
        data_budget = budget_sheet.get_all_records()
        df_budget = pd.DataFrame(data_budget)
        response = ""
        for index, budget in df_budget.iterrows():
            response += f"*Presupuesto {budget['numero_presupuesto']}*\n*Descripción*: {budget['descripcion']}\n*Proveedor*: {budget['nombre_proveedor']}\n*Monto*: {budget['monto']} {budget['moneda']}\n*Saldo*: {budget['monto_pendiente']} {budget['moneda']}\n\n"

        return response
    
    def update_cell(self, sheet, id, column, value):
        # Actualizo la columna "columna" del id 
        cell = sheet.find(id, in_column=1)
        row_index = cell.row
        column = sheet.find(column, in_row=1)
        column_index = column.col
        sheet.update_cell(row_index, column_index, value)


    def create_pdf_from_spreadsheet(self):

        data = {}

        providers_ws = self.sh.worksheet('Proveedores')
        providers_values = providers_ws.get_all_values()
        providers_df = pd.DataFrame(providers_values[1:], columns=providers_values[0])
        data['Proveedores'] = providers_df

        budgets_ws = self.sh.worksheet('Presupuestos')
        budgets_values = budgets_ws.get_all_values()
        budgets_df = pd.DataFrame(budgets_values[1:], columns=budgets_values[0])
        data['Presupuestos'] = budgets_df

        payments_ws = self.sh.worksheet('Pagos')
        payments_values = payments_ws.get_all_values()
        payments_df = pd.DataFrame(payments_values[1:], columns=payments_values[0])
        data['Pagos'] = payments_df
        
        with open("/tmp/data.txt", 'w') as txt_file:
        # Agregar los datos de la hoja de cálculo al archivo de texto
            for sheet_name, df in data.items():
                txt_file.write(f"Datos de la hoja: {sheet_name}\n")
                for index, row in df.iterrows():
                    for col_name, value in row.items():
                        txt_file.write(f"{col_name}: {value}\n")
                    txt_file.write("\n")  # Salto de línea entre cada proveedor

        return True
        
    
    def format_message(self):
        message_array = self.message.splitlines()
        # El titulo del mensaje debe de ser el nombre de la hoja en la que se quiere guardar la info
        self.sheet = message_array[0]

    def read_data(self, range): #range = "A1:E1". Data devolvera un array de la fila 1 desde la columna A hasta la E
        data = self.sheet.get(range)
        return data

    def read_data_by_uid(self, uid):
        data = self.sheet.get_all_records()
        df = pd.DataFrame(data)
        print(df)
        filtered_data = df[df['uid'] == uid]
        return filtered_data #devuelve un data frame de una tabla, de dos filas siendo la primera las cabeceras de las columnas y la segunda los valores filtrados para acceder a un valor en concreto df["nombre"].to_string()
    
    def write_data(self, range, values): #range ej "A1:V1". values must be a list of list
        self.sheet.update(range, values)

    def write_data_by_uid(self, uid, values): 
        # Find the row index based on the UID
        cell = self.sheet.find(uid)
        row_index = cell.row
        # Update the row with the specified values
        self.sheet.update("A{}:E{}".format(row_index, row_index), values)

    def get_last_row_range(self):   
        last_row = len(self.sheet.get_all_values()) + 1
        deta = self.sheet.get_all_values()
        range_start = "A{}".format(last_row)
        letter_end = chr(ord('A') + len(deta[0]) - 1)
        range_end = "{}{}".format(letter_end,last_row)
        return "{}:{}".format(range_start,range_end)
    
    def get_all_values(self):
        #self.sheet.get_all_values () # this return a list of list, so the get all records is easier to get values filtering
        return self.sheet.get_all_records() # this return a list of dictioraies so the key is the name column and the value is the value for that particular column
    