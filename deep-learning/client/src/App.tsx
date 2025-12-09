import { useState } from 'react'
import Form from './components/Form'
import Prediction from './components/Prediction'
import type { PredictionResponse } from './types'
import './App.css'

function App() {
  const [predictionData, setPredictionData] = useState<PredictionResponse | null>(null)

  const handleSubmitSuccess = (data: PredictionResponse) => {
    setPredictionData(data)
  }

  return (
    <>
      <div style={{ 
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 40px'
      }}>
        <header className="app-header">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px', marginBottom: '10px' }}>
            <img 
              src="https://www.cap-com.org/sites/default/files/styles/image_grid_style/public/2019-01/nvlogoparis.jpg?itok=-7R9U5G_" 
              alt="Logo Ville de Paris" 
              style={{ height: '80px', width: 'auto', objectFit: 'contain' }}
            />
            <h1 className="app-title" style={{ margin: 0 }}>Particip'action</h1>
          </div>
          <p className="app-subtitle">Analyse intelligente de vos projets participatifs</p>
        </header>
      </div>
      <div style={{ 
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 40px 40px'
      }}>
        <Form onSubmitSuccess={handleSubmitSuccess} />
        <div style={{ marginTop: '30px' }}>
          <Prediction data={predictionData} />
        </div>
      </div>
    </>
  )
}

export default App
