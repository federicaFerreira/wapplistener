# from app.models.declarative_base import engine, Base, session
# from app.models.message import Message
# from app.models.contact import Contact
import json
import logging

class Whatsapp():

    # def __init__(self):
    #     Base.metadata.create_all(engine)

    def add_contact(self, whatsapp_id, whatsapp_name):
        # busqueda = session.query(Contact).filter(Contact.whatsapp_id == whatsapp_id).all()
        # if len(busqueda) == 0:
        #     contact = Contact(whatsapp_id=whatsapp_id, whatsapp_name=whatsapp_name)
        #     session.add(contact)
        #     session.commit()
        return True
        # else:
        #     return False
    
    def process_message(self, text):
        
        # msg = Message(text=text)
        # session.add(msg)
        # session.commit()

        try:
            response = 'NO_TYPE'
            splited_message = text.splitlines()

            if (splited_message[0] == 'Link de pago de presupuesto'):
                budget = splited_message[1].split(":")
                amount = splited_message[2].split(":")
                currency = splited_message[3].split(":")
                self.type_params = {
                    "budget_code": budget[1].strip(),
                    "amount": amount[1].strip(),
                    "currency": currency[1].strip()
                }
                response = "BUDGET_PAYMENT_LINK"

            if (splited_message[0] == 'Link de pago'):
                provider = splited_message[1].split(":")
                amount = splited_message[2].split(":")
                currency = splited_message[3].split(":")
                self.type_params = {
                    "provider_code": provider[1].strip(),
                    "amount": amount[1].strip(),
                    "currency": currency[1].strip()
                }
                response = 'PROVIDER_PAYMENT_LINK'

            if (splited_message[0] == 'Conciliar pago'):
                budget = splited_message[1].split(":")
                amount = splited_message[2].split(":")
                currency = splited_message[3].split(":")
                self.type_params = {
                    "budget_code": budget[1].strip(),
                    "amount": amount[1].strip(),
                    "currency": currency[1].strip()
                }
                response = 'RECONCILE_PAYMENT'

            if (splited_message[0] == 'Pago'):
                provider = splited_message[1].split(":")
                amount = splited_message[2].split(":")
                currency = splited_message[3].split(":")
                self.type_params = {
                    "provider_code": provider[1].strip(),
                    "amount": amount[1].strip(),
                    "currency": currency[1].strip()
                }
                response = 'PAYMENT'
            
            if (splited_message[0] == 'Proveedores' or splited_message[0] == 'proveedores'):
                response = 'PROVIDERS'
            
            if (splited_message[0] == 'Presupuestos' or splited_message[0] == 'presupuestos'):
                response = 'BUDGETS'
            
            if (splited_message[0] == 'Actualizar'):
                response = 'UPDATE_DATA'
            
            logging.info(f"Parser response: {response}")
            return response
        except:
            response = 'ERROR'
            logging.info(f"ERROR message data: {text}")
            return response
    