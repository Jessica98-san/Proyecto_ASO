import config from "./config.json";
const baseUrlEnv = import.meta.env.VITE_API_URL
const portEnv = import.meta.env.VITE_PORT

const BASE_URL = `${baseUrlEnv}:${portEnv}`?(baseUrlEnv && portEnv): config.BASE_URL;

const getHealthCheck = async () => {
    try {
        console.log(BASE_URL);
        const response = await fetch(`${BASE_URL}/health`);
        // Response {"status": "OK"}
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
        alert("El backend no esta en ejecucion");
    }
}

const saveData = async (mensaje,autor) => {
    try {
        const response = await fetch(`${BASE_URL}/save`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ mensaje, autor })
        });
        return true;
    } catch (error) {
        console.error(error);
        alert("No se pudo guardar datos del backend");
    }
}

const getData = async () => {
    try {
        const response = await fetch(`${BASE_URL}/data`);
        // Response [{"mensaje":"OK","autor":"somebody"}]
        const data = await response.json();
        return data?data:[];

    } catch (error) {
        console.error(error);
        alert("No se pudo obtener datos del backend");
    }
}

export { getHealthCheck, getData, saveData };
