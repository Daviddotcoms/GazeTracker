import sys
if not hasattr(sys, 'frozen'):
    sys.frozen = False
if not hasattr(sys, 'frozen_d'):
    sys.frozen_d = False
from formularios.form_maestro_design import FormularioMaestroDesign
from util.util_paths import resource_path
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(resource_path(".")))
    app = FormularioMaestroDesign()
    app.mainloop()
