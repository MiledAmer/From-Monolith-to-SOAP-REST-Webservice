from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.complex import ComplexModel
from spyne.model.fault import Fault
from wsgiref.simple_server import make_server
import logging
import models

class ProductModel(ComplexModel):
    id = Integer
    name = Unicode
    quantity_in_stock = Integer
    price_per_unit = Float

class InventoryService(ServiceBase):

    @rpc(Unicode, Integer, Float, _returns=ProductModel)
    def CreateProduct(ctx, name, quantity_in_stock, price_per_unit):
        if quantity_in_stock < 0:
            raise Fault(faultcode="Client", faultstring="Quantity cannot be negative")
        
        try:
            new_prod = models.createProduct(name, quantity_in_stock, price_per_unit)
            return new_prod
        except Exception as e:
            raise Fault(faultcode="Server", faultstring=str(e))

    @rpc(Integer, _returns=ProductModel)
    def GetProduct(ctx, product_id):
        product = models.readProduct(product_id)
        if not product:
            raise Fault(faultcode="Client", faultstring=f"Product ID {product_id} not found")
        return product

    @rpc(Integer, Unicode, Integer, Float, _returns=ProductModel)
    def UpdateProduct(ctx, product_id, name=None, quantity_in_stock=None, price_per_unit=None):
        if quantity_in_stock is not None and quantity_in_stock < 0:
            raise Fault(faultcode="Client", faultstring="Quantity cannot be negative")

        updated_prod = models.updateProduct(product_id, name, quantity_in_stock, price_per_unit)
        
        if not updated_prod:
            raise Fault(faultcode="Client", faultstring=f"Product ID {product_id} not found")
        
        return updated_prod

    @rpc(Integer, _returns=Unicode)
    def DeleteProduct(ctx, product_id):
        success = models.deleteProduct(product_id)
        if not success:
            raise Fault(faultcode="Client", faultstring=f"Product ID {product_id} not found")
        return f"Product {product_id} deleted successfully"

def create_app():
    models.create_tables()
    
    application = Application(
        [InventoryService],
        tns='spyne.examples.inventory',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    
    return WsgiApplication(application)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.INFO)

    app = create_app()
    
    host = 'localhost'
    port = 8000
    
    print(f"SOAP Service listening on http://{host}:{port}")
    print(f"WSDL available at http://{host}:{port}/?wsdl")
    
    server = make_server(host, port, app)
    server.serve_forever()