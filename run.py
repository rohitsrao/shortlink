from url_shortener import app

import os
print(os.environ['RUN_ENV'])

if __name__ == '__main__':
    if (os.environ['RUN_ENV'] == 'DEV'): app.run(debug=True, host='0.0.0.0')
    if (os.environ['RUN_ENV'] == 'PROD'): app.run(host='0.0.0.0')
