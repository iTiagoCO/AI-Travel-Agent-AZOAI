# ✈️🧳 Agente de Viajes AI- Impulsado por LangGraph 🌍

¡Bienvenido al repositorio de **Agente de Viajes AI**! Este proyecto demuestra cómo aprovechar **LangGraph** junto con **Azure OpenAI** y **LangChain** para construir un asistente de viajes inteligente que automatiza tareas como la búsqueda de vuelos, la reserva de hoteles y el envío de correos electrónicos personalizados. El agente está diseñado para proporcionar a los usuarios una experiencia fluida de planificación de viajes mediante el uso inteligente de múltiples modelos de lenguaje y APIs.

## **Características**

- **Interacciones con Estado**: El agente recuerda las interacciones del usuario y continúa desde donde lo dejó, asegurando una experiencia personalizada y fluida.
- **Human-in-the-Loop**: Los usuarios pueden intervenir en etapas críticas (como revisar los planes de viaje antes de enviar los correos electrónicos) para tener control total sobre la experiencia.
- **Uso Dinámico de Modelos de Lenguaje**: El agente cambia de manera inteligente entre múltiples modelos de lenguaje, incluidos los de **Azure OpenAI**, para tareas como la invocación de herramientas, reservas de vuelos y generación de correos electrónicos.
- **Automatización de Correos Electrónicos**: Genera automáticamente planes de viaje detallados y los envía por correo electrónico.
- **Integración con APM**: Supervisa el rendimiento del agente y rastrea las interacciones utilizando herramientas de Monitoreo de Rendimiento de Aplicaciones (APM) para asegurar que el agente funcione de manera fluida y confiable.

## **Cómo Empezar**

Sigue estos pasos para configurar el proyecto en tu entorno local.

1. Clona el repositorio:
   ```bash
   git clone https://github.com/iTiagoCO/AI-Travel-Agent-AZOAI.git


1. ( (Opcional) Configura tu versión de Python usando pyenv si estás utilizando Python 3.11.9 )
   ```shell script
   pyenv local 3.11.9
   ```

1. Instala las dependencias del proyecto:
    ```shell script
    poetry install --sync
    ```

1. Entra al entorno virtual:
    ```shell script
    poetry shell
    ```

## **Guarda Tus Claves API**

1. Crea un archivo `.env` en el directorio raíz del proyecto. 
2. Agrega tus claves API y variables de entorno al archivo `.env`:
    ```plaintext
    AZURE_OPENAI_KEY=
    AZURE_OPENAI_ENDPOINT=
    AZURE_DEPLOYMENT_NAME=
    SERPAPI_API_KEY=
    SENDGRID_API_KEY=

    # Observability variables
    LANGCHAIN_API_KEY=
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_PROJECT=ai_travel_agent
    ```

Asegúrate de reemplazar los valores de las claves.

### Cómo Ejecutar el Chatbot
Para iniciar el chatbot, ejecuta el siguiente comando:
```
streamlit run app.py
```

### Usando el Chatbot
Una vez lanzado, simplemente ingresa tu solicitud de viaje. Por ejemplo:
> Quiero viajar a Ámsterdam desde Madrid del 1 al 2 de Diciembre. Encuentra vuelos y hoteles de 4 estrellas.

![image](https://github.com/user-attachments/assets/cd6377cf-0ece-4b87-8e47-25661a8714a7)


El chatbot generará resultados que incluyen logotipos y enlaces para facilitar la navegación.

> **Note**: Nota: Los datos se obtienen a través de las APIs de Google Flights y Google Hotels. No hay afiliación ni promoción de ninguna marca en particular.


#### Example Outputs

- Opciones de vuelos y hoteles con logotipos relevantes y enlaces para fácil referencia:



## License
Distribuido bajo la Licencia MIT. Consulta el archivo LICENSE.txt para más información.
