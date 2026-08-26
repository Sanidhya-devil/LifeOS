import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { MorningDashboard } from './pages/MorningDashboard';
import { ReviewToday } from './pages/ReviewToday';
import { PlanTomorrow } from './pages/PlanTomorrow';
import { TasksManager } from './pages/TasksManager';
import { FixedSchedulePage } from './pages/FixedSchedulePage';

export function App() {
  const [activeTab, setActiveTab] = useState<'morning' | 'review' | 'planner' | 'tasks' | 'fixed'>('morning');
  const [lastReviewId, setLastReviewId] = useState<number | undefined>(undefined);
  const [userLevel, setUserLevel] = useState<number>(12);
  const [totalXp, setTotalXp] = useState<number>(170);

  const handleProceedToPlan = (reviewId?: number) => {
    setLastReviewId(reviewId);
    setActiveTab('planner');
    // Bump XP locally for immediate visual feedback
    setTotalXp((prev) => prev + 50);
  };

  const handlePlanApproved = () => {
    setActiveTab('morning');
  };

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        userLevel={userLevel}
        totalXp={totalXp}
      />

      {/* Main Page Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activeTab === 'morning' && (
          <MorningDashboard
            onNavigateToReview={() => setActiveTab('review')}
            onNavigateToPlan={() => setActiveTab('planner')}
          />
        )}
        {activeTab === 'review' && (
          <ReviewToday
            onProceedToPlan={handleProceedToPlan}
          />
        )}
        {activeTab === 'planner' && (
          <PlanTomorrow
            initialReviewId={lastReviewId}
            onPlanApproved={handlePlanApproved}
          />
        )}
        {activeTab === 'tasks' && <TasksManager />}
        {activeTab === 'fixed' && <FixedSchedulePage />}
      </main>

      {/* Sleek Footer */}
      <footer className="border-t border-slate-800/80 py-6 mt-12 bg-surface/50 text-center text-xs text-slate-500">
        <p>LifeOS — Local-First Agentic AI Daily Life Operating System • Deterministic Core + LangGraph Agent</p>
      </footer>
    </div>
  );
}

export default App;
