import { getHealthCheck, getData, saveData } from "./services"
import { useState } from "react";
import "./App.css";

const App = () => {

  const [mensaje, setMensaje] = useState("");
  const [data, setData] = useState([]);
  const [autor_form, setAutor_form] = useState("");
  const [mensaje_form, setMensaje_form] = useState("");

  const serviceHealtCheck = async () => {
    const data = await getHealthCheck();
    console.log(data);
    if (data) {
      setMensaje("El backend esta en ejecucion");
    }
  }

  const serviceGetData = async () => {
    const data = await getData();
    console.log(data);
    // Response [{"mensaje":"OK","autor":"somebody"}]
    if (data) {
      setData(data);
      setMensaje("Datos obtenidos correctamente");
    }
  }

  const serviceSaveData = async () => {
    if (!autor_form || !mensaje_form) {
      alert("Por favor, complete todos los campos");
      return;
    }
    const save_flag = await saveData(mensaje_form, autor_form);
    console.log(save_flag);
    if (save_flag) {
      setMensaje("Datos guardados correctamente");
      setAutor_form("");
      setMensaje_form("");
    }
  }

  return (<>
    <h1>Frondend Web</h1>
    <h2>{`Mensaje: ${mensaje || 'No hay mensajes'}`}</h2>

    <div className="container">
      <h2>Probar Health Check</h2>
      <button onClick={serviceHealtCheck}>Comprobar Health Check</button>
      <button onClick={() => { setMensaje("") }}>Limpiar mensajes</button>
    </div>

    <div className="container">
      <h2>Guardar Data</h2>
      <input type="text" placeholder="Autor" value={autor_form} onChange={(e) => setAutor_form(e.target.value)} />
      <input type="text" placeholder="Mensaje" value={mensaje_form} onChange={(e) => setMensaje_form(e.target.value)} />
      <button onClick={serviceSaveData}>Guardar Data</button>

      <h2>Obtener Data</h2>
      <button onClick={serviceGetData}>Obtener Data</button>
      <button onClick={() => { setData([]) }}>Limpiar data</button>
      {
        data.map((item, index) => (
          <div key={index} className="card">
            <p>{item.mensaje}</p>
            <p>{item.autor}</p>
          </div>
        ))
      }
    </div>
  </>
  )
}

export default App
