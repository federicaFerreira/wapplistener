import logging
import os
from app import create_app


app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    app.run()#host="0.0.0.0", port=8081) #port=8000)



