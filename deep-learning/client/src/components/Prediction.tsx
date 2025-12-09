import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import type { PredictionResponse, ProjectExample } from '../types';

interface PredictionProps {
  data: PredictionResponse | null;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];
const STATUS_COLORS = {
  abandoned: '#FF4444',
  inProgress: '#FFA500',
  completed: '#00C851'
};

function Prediction({ data }: PredictionProps) {
  if (!data) {
    return (
      <div className="prediction-container">
        <h2>Résultat de l'analyse</h2>
        <p style={{ color: '#6c757d', fontStyle: 'italic' }}>
          En attente d'une analyse...
        </p>
      </div>
    );
  }

  const { predictedCategory } = data;
  const { metrics } = predictedCategory;

  return (
    <div className="prediction-container" style={{ maxHeight: '90vh', overflowY: 'auto' }}>
      <h2>Résultat de l'analyse</h2>
      
      {/* Catégorie prédite - Mise en avant */}
      <div className="predicted-category-highlight">
        <h2 className="predicted-category-title">Catégorie prédite</h2>
        
        {/* Titre du projet */}
        <div style={{
          fontSize: '16px',
          color: '#adb5bd',
          marginBottom: '15px',
          fontWeight: '500'
        }}>
          Projet : <span style={{ color: '#e9ecef' }}>{predictedCategory.projectTitle}</span>
        </div>
        
        <div className="predicted-category-name">🎯 {predictedCategory.name}</div>
        
        <div className="predicted-category-stats">
          <div className="predicted-category-stat">
            <div className="predicted-category-stat-label">Confiance</div>
            <div className="predicted-category-stat-value">
              {(predictedCategory.confidence * 100).toFixed(1)}%
            </div>
          </div>
        </div>
        
        <p style={{ 
          margin: '20px 0 0 0', 
          padding: '15px', 
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '8px',
          color: '#e9ecef',
          lineHeight: '1.6',
          textAlign: 'center',
          fontStyle: 'italic'
        }}>
          {predictedCategory.analyse}
        </p>
      </div>

      {!metrics ? (
        <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Aucune métrique disponible</p>
      ) : (
        <>
          {/* Période */}
          <div style={{ marginBottom: '20px' }}>
            <h3>Période d'analyse</h3>
            <p>{metrics.startingYear} - {metrics.endingYear} ({metrics.numberOfRecords} enregistrements)</p>
          </div>

          {/* Statuts des projets */}
          <div style={{ marginBottom: '30px' }}>
            <h3>Statuts des projets</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={(() => {
                    const total = metrics.statuses.pieChart.abandoned + 
                                  metrics.statuses.pieChart.inProgress + 
                                  metrics.statuses.pieChart.completed;
                    return [
                      { 
                        name: 'Abandonné', 
                        value: total > 0 ? Math.round((metrics.statuses.pieChart.abandoned / total) * 100) : 0
                      },
                      { 
                        name: 'En cours', 
                        value: total > 0 ? Math.round((metrics.statuses.pieChart.inProgress / total) * 100) : 0
                      },
                      { 
                        name: 'Terminé', 
                        value: total > 0 ? Math.round((metrics.statuses.pieChart.completed / total) * 100) : 0
                      }
                    ];
                  })()}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  label={(entry) => `${entry.name}: ${entry.value}%`}
                >
                  <Cell fill={STATUS_COLORS.abandoned} />
                  <Cell fill={STATUS_COLORS.inProgress} />
                  <Cell fill={STATUS_COLORS.completed} />
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>

            {/* Exemples de projets abandonnés */}
            <div style={{ marginTop: '20px' }}>
              <h4>Exemples de projets abandonnés</h4>
              <ProjectTable projects={metrics.statuses.abandonedExamples} />
            </div>
          </div>

          {/* Distribution par code postal */}
          <div style={{ marginBottom: '30px' }}>
            <h3>Distribution par code postal</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics.postalCodeDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="postalCode" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" name="Nombre de projets" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Zones prioritaires */}
          <div style={{ marginBottom: '30px' }}>
            <h3>Zones prioritaires</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={(() => {
                    const total = metrics.priorityArea.highPriority + metrics.priorityArea.lowPriority;
                    return [
                      { 
                        name: 'Haute priorité', 
                        value: total > 0 ? Math.round((metrics.priorityArea.highPriority / total) * 100) : 0
                      },
                      { 
                        name: 'Basse priorité', 
                        value: total > 0 ? Math.round((metrics.priorityArea.lowPriority / total) * 100) : 0
                      }
                    ];
                  })()}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  label={(entry) => `${entry.name}: ${entry.value}%`}
                >
                  <Cell fill="#FF6B6B" />
                  <Cell fill="#4ECDC4" />
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Budget */}
          <div style={{ marginBottom: '30px' }}>
            <h3>Analyse des budgets</h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(2, 1fr)', 
              gap: '15px',
              marginBottom: '20px'
            }}>
              <BudgetCard label="Médian" value={metrics.budget.median} />
              <BudgetCard label="Moyen" value={metrics.budget.average} />
              <BudgetCard label="Minimum" value={metrics.budget.min} />
              <BudgetCard label="Maximum" value={metrics.budget.max} />
            </div>

            <div style={{ marginTop: '20px' }}>
              <h4>5 projets les plus chers</h4>
              <ProjectTable projects={metrics.budget.fiveMostExpensive} />
            </div>

            <div style={{ marginTop: '20px' }}>
              <h4>5 projets les moins chers</h4>
              <ProjectTable projects={metrics.budget.fiveLeastExpensive} />
            </div>

            {/* Position du budget par quartile */}
            <div style={{ marginTop: '30px' }}>
              <h4>Positionnement du budget</h4>
              
              {/* Affichage du budget estimé */}
              <div style={{
                padding: '15px',
                backgroundColor: '#1a1a1a',
                borderRadius: '12px',
                border: '1px solid #495057',
                marginBottom: '20px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '14px', color: '#adb5bd', marginBottom: '5px' }}>
                  Budget estimé de votre projet
                </div>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#4dabf7' }}>
                  {predictedCategory.estimatedBudget.toLocaleString('fr-FR')} €
                </div>
              </div>

              {metrics.budget.position.estimatedBudgetQuartile !== null && (
                <div style={{
                  padding: '15px',
                  backgroundColor: '#2d2d2d',
                  borderRadius: '12px',
                  border: '2px solid #4dabf7',
                  marginBottom: '20px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '14px', color: '#adb5bd', marginBottom: '5px' }}>
                    Votre budget se situe dans le
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4dabf7' }}>
                    Quartile {metrics.budget.position.estimatedBudgetQuartile}
                  </div>
                </div>
              )}
              
              <div style={{ 
                display: 'grid', 
                gap: '15px',
                marginTop: '15px'
              }}>
                {metrics.budget.position.quartiles.map((quartile) => (
                  <div 
                    key={quartile.quartile}
                    style={{
                      padding: '15px',
                      backgroundColor: quartile.quartile === metrics.budget.position.estimatedBudgetQuartile 
                        ? 'rgba(77, 171, 247, 0.2)' 
                        : '#1a1a1a',
                      borderRadius: '8px',
                      border: quartile.quartile === metrics.budget.position.estimatedBudgetQuartile 
                        ? '2px solid #4dabf7' 
                        : '1px solid #495057',
                      boxShadow: quartile.quartile === metrics.budget.position.estimatedBudgetQuartile 
                        ? '0 4px 12px rgba(77, 171, 247, 0.3)' 
                        : 'none'
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      marginBottom: '10px'
                    }}>
                      <div style={{ 
                        fontSize: '18px', 
                        fontWeight: 'bold', 
                        color: quartile.quartile === metrics.budget.position.estimatedBudgetQuartile 
                          ? '#4dabf7' 
                          : '#e9ecef'
                      }}>
                        {quartile.label}
                      </div>
                      <div style={{
                        padding: '4px 12px',
                        backgroundColor: '#2d2d2d',
                        borderRadius: '12px',
                        fontSize: '12px',
                        color: '#adb5bd'
                      }}>
                        Q{quartile.quartile}
                      </div>
                    </div>
                    
                    <div style={{ 
                      display: 'flex', 
                      gap: '20px', 
                      marginBottom: '10px',
                      fontSize: '14px',
                      color: '#adb5bd'
                    }}>
                      <div>
                        <span style={{ color: '#6c757d' }}>Min: </span>
                        <span style={{ fontWeight: '500', color: '#e9ecef' }}>
                          {quartile.min.toLocaleString('fr-FR')} €
                        </span>
                      </div>
                      <div>
                        <span style={{ color: '#6c757d' }}>Max: </span>
                        <span style={{ fontWeight: '500', color: '#e9ecef' }}>
                          {quartile.max.toLocaleString('fr-FR')} €
                        </span>
                      </div>
                    </div>
                    
                    <div style={{ 
                      fontSize: '13px', 
                      color: '#adb5bd',
                      fontStyle: 'italic',
                      lineHeight: '1.4'
                    }}>
                      {quartile.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Composant pour afficher une carte de budget
function BudgetCard({ label, value }: { label: string; value: number }) {
  return (
    <div style={{
      backgroundColor: '#2d2d2d',
      padding: '15px',
      borderRadius: '12px',
      border: '1px solid #495057',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
    }}>
      <div style={{ fontSize: '14px', color: '#adb5bd', marginBottom: '5px' }}>{label}</div>
      <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#4dabf7' }}>
        {value.toLocaleString('fr-FR')} €
      </div>
    </div>
  );
}

// Composant pour afficher un tableau de projets
function ProjectTable({ projects }: { projects: ProjectExample[] }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: '14px'
      }}>
        <thead>
          <tr style={{ backgroundColor: '#2d2d2d' }}>
            <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #495057', color: '#e9ecef' }}>Titre</th>
            <th style={{ padding: '12px', textAlign: 'right', border: '1px solid #495057', color: '#e9ecef' }}>Budget</th>
            <th style={{ padding: '12px', textAlign: 'center', border: '1px solid #495057', color: '#e9ecef' }}>Année</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((project, index) => (
            <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#1a1a1a' : '#242424' }}>
              <td style={{ padding: '12px', border: '1px solid #495057', color: '#adb5bd' }}>{project.title}</td>
              <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #495057', color: '#4dabf7', fontWeight: '500' }}>
                {project.budget.toLocaleString('fr-FR')} €
              </td>
              <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #495057', color: '#adb5bd' }}>
                {project.year}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Prediction;
