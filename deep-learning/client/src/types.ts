// Types pour la réponse de l'API de prédiction

export interface CategoryBreakdown {
  category: string;
  percentage: number;
  selected: boolean;
  [key: string]: any;
}

export interface PostalCodeDistribution {
  postalCode: string;
  count: number;
}

export interface StatusPieChart {
  abandoned: number;
  inProgress: number;
  completed: number;
}

export interface ProjectExample {
  title: string;
  budget: number;
  year: string;
}

export interface Statuses {
  pieChart: StatusPieChart;
  abandonedExamples: ProjectExample[];
}

export interface PriorityArea {
  highPriority: number;
  lowPriority: number;
}

export interface Quartile {
  quartile: number;
  label: string;
  min: number;
  max: number;
  description: string;
}

export interface Position {
  quartiles: Quartile[];
  estimatedBudgetQuartile: number | null;
}

export interface Budget {
  median: number;
  average: number;
  min: number;
  max: number;
  fiveMostExpensive: ProjectExample[];
  fiveLeastExpensive: ProjectExample[];
  position: Position;
}

export interface Metrics {
  startingYear: number;
  endingYear: number;
  numberOfRecords: number;
  breakdownByCategory: CategoryBreakdown[];
  postalCodeDistribution: PostalCodeDistribution[];
  statuses: Statuses;
  priorityArea: PriorityArea;
  budget: Budget;
}

export interface PredictedCategory {
  name: string;
  confidence: number;
  analyse: string;
  projectTitle: string;
  estimatedBudget: number;
  metrics: Metrics | null;
}

export interface PredictionResponse {
  predictedCategory: PredictedCategory;
}
