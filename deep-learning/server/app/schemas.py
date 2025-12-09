from pydantic import BaseModel
from typing import List, Optional

# ============== Utils Models ==============
class PredictionInfo(BaseModel):
    name: str
    confidence: float
    analyse: str

# ============== Request Models ==============
class PredictRequest(BaseModel):
    projectTitle: str
    estimatedBudget: int

# ============== Response Models ==============
class CategoryBreakdown(BaseModel):
    category: str
    percentage: int
    selected: bool

class PostalCodeDistribution(BaseModel):
    postalCode: str
    count: int

class ProjectExample(BaseModel):
    title: str
    budget: int
    year: str

class StatusesPieChart(BaseModel):
    abandoned: int
    inProgress: int
    completed: int

class Statuses(BaseModel):
    pieChart: StatusesPieChart
    abandonedExamples: List[ProjectExample]

class PriorityArea(BaseModel):
    highPriority: int
    lowPriority: int

class Quartile(BaseModel):
    quartile: int
    label: str
    min: int
    max: int
    description: str

class Position(BaseModel):
    quartiles: List[Quartile]
    estimatedBudgetQuartile: Optional[int]

class Budget(BaseModel):
    median: int
    average: int
    min: int
    max: int
    fiveMostExpensive: List[ProjectExample]
    fiveLeastExpensive: List[ProjectExample]
    position: Position

class Metrics(BaseModel):
    startingYear: int
    endingYear: int
    numberOfRecords: int
    breakdownByCategory: List[CategoryBreakdown]
    postalCodeDistribution: List[PostalCodeDistribution]
    statuses: Statuses
    priorityArea: PriorityArea
    budget: Budget

class PredictedCategory(BaseModel):
    name: str
    confidence: float
    analyse: str
    projectTitle: str
    estimatedBudget: int
    metrics: Optional[Metrics]

class PredictResponse(BaseModel):
    predictedCategory: PredictedCategory
