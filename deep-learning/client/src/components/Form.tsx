import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import type { PredictionResponse } from '../types'

interface FormData {
  projectTitle: string
  estimatedBudget: number
}

interface FormProps {
  onSubmitSuccess: (data: PredictionResponse) => void
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Form({ onSubmitSuccess }: FormProps) {
  const [titre, setTitre] = useState<string>('')
  const [budget, setBudget] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const handleTitreChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const words = e.target.value.trim().split(/\s+/).filter(word => word.length > 0)
    if (words.length <= 15 || e.target.value === '') {
      setTitre(e.target.value)
    }
  }

  const wordCount = titre.trim().split(/\s+/).filter(word => word.length > 0).length

  const handleBudgetChange = (e: ChangeEvent<HTMLInputElement>): void => {
    setBudget(e.target.value)
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    
    const formData: FormData = {
      projectTitle: titre,
      estimatedBudget: parseInt(budget, 10)
    }
    
    try {
      const response = await fetch(`${API_URL}/predict-category`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }

      const data: PredictionResponse = await response.json()
      
      onSubmitSuccess(data)
      
      // Réinitialiser le formulaire en cas de succès
      setTitre('')
      setBudget('')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Une erreur est survenue'
      setError(errorMessage)
      console.error('Erreur lors de l\'envoi:', errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="form-container">
      <h1>Analyser un nouveau projet</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="titre">
            Titre du projet <span style={{ color: '#6c757d', fontSize: '14px' }}>({wordCount}/15 mots)</span>
          </label>
          <input
            id="titre"
            type="text"
            value={titre}
            onChange={handleTitreChange}
            placeholder="Décrivez votre projet en quelques mots..."
            required
            disabled={isLoading}
          />
          {wordCount >= 15 && (
            <span style={{ fontSize: '12px', color: '#ffa94d', marginTop: '5px', display: 'block' }}>
              Limite de 15 mots atteinte
            </span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="budget">
            Budget prévisionnel
          </label>
          <input
            id="budget"
            type="number"
            value={budget}
            onChange={handleBudgetChange}
            min="0"
            step="1"
            placeholder="Ex: 50000"
            required
            disabled={isLoading}
          />
        </div>

        {error && (
          <div style={{ 
            padding: '12px', 
            marginBottom: '20px', 
            backgroundColor: '#fee', 
            color: '#c33', 
            borderRadius: '4px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {isLoading && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            gap: '12px'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #3498db',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <span style={{ color: '#666', fontSize: '16px' }}>Analyse en cours...</span>
          </div>
        )}

        <button type="submit" className="submit-btn" disabled={isLoading}>
          {isLoading ? 'Envoi en cours...' : 'Analyser le projet'}
        </button>
      </form>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default Form
